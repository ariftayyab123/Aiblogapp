"""Provider-neutral blog generation orchestration."""
import time
import re
from typing import Dict, List, Any, Optional
from threading import Lock
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from ai_blog.apps.core.services.base import BaseService, ServiceError
from ..content import compute_content_structure
from ..models import BlogPost, Persona
from .llm import GenerationRequest, LLMProviderError, create_llm_provider
from .prompts import PromptService


class BlogGenerationService(BaseService[BlogPost]):
    """Coordinate prompts, persistence, and a configured LLM provider."""

    model_class = BlogPost
    logger_name = "blog_generation"

    MAX_RETRIES = getattr(settings, 'LLM_MAX_RETRIES', 2)
    RETRY_DELAY = 1.0  # seconds
    GENERATION_TIMEOUT = getattr(settings, 'LLM_TIMEOUT', 60)
    FAST_TIMEOUT = int(getattr(settings, 'LLM_FAST_TIMEOUT', 30))
    FAST_MAX_TOKENS = int(getattr(settings, 'FAST_MAX_TOKENS', 650))
    CIRCUIT_FAILURE_THRESHOLD = int(getattr(settings, 'LLM_CIRCUIT_FAILURE_THRESHOLD', 3))
    CIRCUIT_COOL_OFF_SECONDS = int(getattr(settings, 'LLM_CIRCUIT_COOL_OFF_SECONDS', 30))
    _provider_state = {
        'anthropic': {'failures': 0, 'open_until': 0.0},
        'gemini': {'failures': 0, 'open_until': 0.0},
    }
    _state_lock = Lock()

    def __init__(self, api_key: str = None, provider=None):
        super().__init__()
        self.llm_provider = provider or create_llm_provider(api_key=api_key)
        self.provider = self.llm_provider.name
        self.prompt_service = PromptService()

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        BaseService contract implementation.
        Delegates to the main generation workflow.
        """
        return self.generate_post(*args, **kwargs)

    def generate_post(
        self,
        topic: str,
        persona_slug: str,
        owner=None,
        additional_context: Dict = None,
        stream: bool = False,
        speed: str = 'fast'
    ) -> Dict[str, Any]:
        """
        Main entry point for blog generation.

        Returns:
            {
                'success': bool,
                'blog_post_id': int | None,
                'content': str | None,
                'sources': List[Dict],
                'metadata': Dict,
                'error': str | None
            }
        """
        self.log_execution("generate_post", topic=topic, persona=persona_slug)

        try:
            # 1. Validate inputs
            self._validate_generation_input(topic, persona_slug)
            if owner is None:
                raise ServiceError(
                    "Authenticated owner is required for generation.",
                    code="AUTH_REQUIRED"
                )

            # 2. Fetch persona
            persona = self._get_persona(persona_slug)

            # 3. Build prompts
            system_prompt, user_prompt = self.prompt_service.build_generation_prompt(
                topic=topic,
                persona=persona,
                additional_context=additional_context or {},
                speed=speed
            )

            # 4. Create BlogPost record in GENERATING state
            blog_post = self._create_post_record(
                topic=topic,
                persona=persona,
                raw_prompt=user_prompt,
                owner=owner,
            )

            # 5. Generate content through the configured provider adapter
            response_data = self._call_model_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=persona.temperature,
                max_tokens=self._resolve_max_tokens(persona.max_tokens, speed),
                speed=speed
            )

            # 6. Parse response
            parsed_content = self._parse_response(response_data['content'])

            # 7. Update BlogPost with generated content
            self._update_post_with_content(
                blog_post=blog_post,
                content=parsed_content['markdown'],
                sources=parsed_content['sources'],
                structure=parsed_content.get('structure', {}),
                metadata=response_data.get('usage', {}),
                title=parsed_content.get('title'),
            )

            return {
                'success': True,
                'blog_post_id': blog_post.id,
                'status': 'completed',
                'content': parsed_content['markdown'],
                'sources': parsed_content['sources'],
                'metadata': blog_post.metadata
            }

        except ServiceError:
            # Update post status to failed if it exists
            if 'blog_post' in locals():
                blog_post.status = BlogPost.PostStatus.FAILED
                blog_post.save()
            raise
        except Exception as e:
            if 'blog_post' in locals():
                blog_post.status = BlogPost.PostStatus.FAILED
                blog_post.metadata = blog_post.metadata or {}
                blog_post.metadata['error'] = str(e)
                blog_post.save()
            raise self.handle_exception(e, context={'topic': topic, 'persona': persona_slug})

    def _resolve_max_tokens(self, persona_max_tokens: int, speed: str) -> int:
        """Cap token budget for lower latency in fast mode."""
        if speed == 'fast':
            return min(persona_max_tokens, self.FAST_MAX_TOKENS)
        return persona_max_tokens

    def _resolve_retry_count(self, speed: str) -> int:
        """Fast mode avoids retries to reduce tail latency."""
        if speed == 'fast':
            return 0
        return self.MAX_RETRIES

    def _resolve_timeout_seconds(self, speed: str) -> int:
        if speed == 'fast':
            return min(self.GENERATION_TIMEOUT, self.FAST_TIMEOUT)
        return self.GENERATION_TIMEOUT

    def _validate_generation_input(self, topic: str, persona_slug: str) -> None:
        """Validate generation inputs"""
        if not topic or len(topic.strip()) < 5:
            raise ServiceError(
                "Topic must be at least 5 characters long",
                code="INVALID_TOPIC"
            )
        if not persona_slug:
            raise ServiceError(
                "Persona slug is required",
                code="INVALID_PERSONA"
            )

    def _get_persona(self, slug: str) -> Persona:
        """Fetch and validate persona"""
        try:
            persona = Persona.objects.get(slug=slug, is_active=True)
            return persona
        except Persona.DoesNotExist:
            raise ServiceError(
                f"Active persona '{slug}' not found",
                code="PERSONA_NOT_FOUND"
            )

    def _call_model_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        speed: str = 'fast'
    ) -> Dict[str, Any]:
        """Call the configured provider with application-level retry policy."""
        self._check_circuit_state()
        max_retries = self._resolve_retry_count(speed)
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                result = self.llm_provider.generate(GenerationRequest(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    speed=speed,
                    timeout_seconds=self._resolve_timeout_seconds(speed),
                ))
                result.setdefault('usage', {})['retry_count'] = attempt
                self._record_success()
                return result
            except LLMProviderError as exc:
                last_error = exc
                self._logger.warning(
                    "%s generation request failed (attempt %s/%s): %s",
                    self.provider,
                    attempt + 1,
                    max_retries + 1,
                    exc,
                )
                if not exc.retryable:
                    raise ServiceError(
                        "Content generation is currently unavailable. Please try again later.",
                        code=exc.code,
                    ) from exc
                if attempt < max_retries:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))

        self._record_failure()
        raise ServiceError(
            "Content generation is temporarily unavailable. Please try again shortly.",
            code="PROVIDER_UNAVAILABLE",
        ) from last_error

    def _check_circuit_state(self) -> None:
        with self._state_lock:
            state = self._provider_state.get(self.provider, {'failures': 0, 'open_until': 0.0})
            if state['open_until'] > time.time():
                retry_after = int(state['open_until'] - time.time())
                raise ServiceError(
                    f"Content generation is temporarily unavailable. Retry in ~{retry_after}s.",
                    code="PROVIDER_UNAVAILABLE",
                    details={'retry_after_seconds': max(retry_after, 1)}
                )

    def _record_success(self) -> None:
        with self._state_lock:
            if self.provider in self._provider_state:
                self._provider_state[self.provider] = {'failures': 0, 'open_until': 0.0}

    def _record_failure(self) -> None:
        with self._state_lock:
            state = self._provider_state.setdefault(self.provider, {'failures': 0, 'open_until': 0.0})
            failures = state['failures'] + 1
            open_until = state['open_until']
            if failures >= self.CIRCUIT_FAILURE_THRESHOLD:
                open_until = time.time() + self.CIRCUIT_COOL_OFF_SECONDS
            self._provider_state[self.provider] = {'failures': failures, 'open_until': open_until}

    def _create_post_record(self, topic: str, persona: Persona, raw_prompt: str, owner) -> BlogPost:
        """Create initial BlogPost in GENERATING state"""
        # Generate unique slug
        base_slug = slugify(topic[:50])
        slug = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        blog_post = BlogPost.objects.create(
            owner=owner,
            title=f"Draft: {topic[:50]}...",
            slug=slug,
            topic_input=topic,
            raw_prompt=raw_prompt,
            persona=persona,
            status=BlogPost.PostStatus.GENERATING
        )
        return blog_post

    def _parse_response(self, raw_content: str) -> Dict[str, Any]:
        """
        Parse an LLM response to extract:
        - Main markdown content
        - Sources/citations (if present)
        - Title (extracted from first heading)
        """
        result = {
            'markdown': raw_content,
            'sources': [],
            'title': None,
            'structure': {}
        }

        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', raw_content, re.MULTILINE)
        if title_match:
            result['title'] = title_match.group(1).strip()

        # Extract sources from structured format
        sources_section = re.search(
            r'##\s*(?:Sources|References|Citations)\s*\n+(.*?)(?=\n##|\n\n*$)',
            raw_content,
            re.DOTALL | re.IGNORECASE
        )

        if sources_section:
            result['sources'] = self._parse_sources(sources_section.group(1))

            # Remove sources section from main content
            result['markdown'] = re.sub(
                r'##\s*(?:Sources|References|Citations).*?(?=\n##|\n\n*$)',
                '',
                raw_content,
                flags=re.DOTALL | re.IGNORECASE
            ).strip()

        # Calculate structure
        result['structure'] = self._analyze_structure(result['markdown'])

        return result

    def _parse_sources(self, sources_text: str) -> List[Dict[str, Any]]:
        """
        Parse sources section into structured list.
        """
        sources = []

        # Pattern: [Title](url) or - [Title](url)
        citation_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(citation_pattern, sources_text)

        for title, url in matches:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')

            sources.append({
                'title': title.strip(),
                'url': url.strip(),
                'domain': domain,
                'is_verified': False,
                'relevance_score': None
            })

        return sources

    def _analyze_structure(self, markdown: str) -> Dict[str, Any]:
        """Analyze markdown structure for frontend rendering"""
        return compute_content_structure(markdown)

    def _update_post_with_content(
        self,
        blog_post: BlogPost,
        content: str,
        sources: List[Dict],
        structure: Dict,
        metadata: Dict,
        title: Optional[str] = None,
    ) -> None:
        """Update BlogPost with generated content and complete generation"""
        blog_post.generated_content = content
        blog_post.sources = sources
        blog_post.content_structure = structure

        # Replace the "Draft: <topic>" placeholder with the generated headline.
        if title:
            blog_post.title = title[:300]

        # Merge metadata
        blog_post.metadata = {**(blog_post.metadata or {}), **metadata}

        # Update status
        blog_post.status = BlogPost.PostStatus.COMPLETED
        blog_post.published_at = timezone.now()

        blog_post.save()

        # Initialize sentiment score (starts at 0)
        blog_post.update_sentiment_score()

    def get_blog_post(self, blog_post_id: int) -> Optional[Dict]:
        """Get a blog post by ID with all details"""
        try:
            post = BlogPost.objects.get(id=blog_post_id)

            return {
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'topic_input': post.topic_input,
                'generated_content': post.generated_content,
                'content_structure': post.content_structure,
                'sources': post.sources,
                'persona': {
                    'id': post.persona.id,
                    'name': post.persona.name,
                    'slug': post.persona.slug,
                    'description': post.persona.description
                } if post.persona else None,
                'status': post.status,
                'sentiment_score': post.sentiment_score,
                'metadata': post.metadata,
                'created_at': post.created_at.isoformat(),
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'word_count': post.word_count,
                'reading_time': post.reading_time
            }
        except BlogPost.DoesNotExist:
            return None

    def delete_blog_post(self, blog_post_id: int) -> bool:
        """Delete a blog post by ID"""
        try:
            post = BlogPost.objects.get(id=blog_post_id)
            post.delete()
            return True
        except BlogPost.DoesNotExist:
            return False

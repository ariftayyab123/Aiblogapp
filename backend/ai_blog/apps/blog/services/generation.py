"""
Blog Generation Service.
Orchestrates blog post generation with Claude AI.
Handles: prompt construction, API communication, response parsing.
"""
import time
import re
import json
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional
from threading import Lock
from anthropic import Anthropic, AnthropicError
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from ai_blog.apps.core.services.base import BaseService, ServiceError
from ..models import BlogPost, Persona
from .prompts import PromptService


class BlogGenerationService(BaseService[BlogPost]):
    """
    Service for orchestrating blog post generation with Claude AI.
    """

    model_class = BlogPost
    logger_name = "blog_generation"

    # Provider configuration
    PROVIDER = getattr(settings, 'LLM_PROVIDER', 'anthropic')

    # Claude model configuration
    DEFAULT_MODEL = getattr(settings, 'CLAUDE_DEFAULT_MODEL', 'claude-3-5-sonnet-20241022')
    FAST_MODEL = getattr(settings, 'CLAUDE_FAST_MODEL', DEFAULT_MODEL)
    MAX_RETRIES = getattr(settings, 'CLAUDE_MAX_RETRIES', 2)
    RETRY_DELAY = 1.0  # seconds
    GENERATION_TIMEOUT = getattr(settings, 'CLAUDE_TIMEOUT', 60)
    FAST_TIMEOUT = int(getattr(settings, 'CLAUDE_FAST_TIMEOUT', 30))
    FAST_MAX_TOKENS = int(getattr(settings, 'FAST_MAX_TOKENS', 650))
    GEMINI_MODEL = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
    GEMINI_FAST_MODEL = getattr(settings, 'GEMINI_FAST_MODEL', GEMINI_MODEL)
    CIRCUIT_FAILURE_THRESHOLD = int(getattr(settings, 'LLM_CIRCUIT_FAILURE_THRESHOLD', 3))
    CIRCUIT_COOL_OFF_SECONDS = int(getattr(settings, 'LLM_CIRCUIT_COOL_OFF_SECONDS', 30))
    _provider_state = {
        'anthropic': {'failures': 0, 'open_until': 0.0},
        'gemini': {'failures': 0, 'open_until': 0.0},
    }
    _state_lock = Lock()

    def __init__(self, api_key: str = None):
        super().__init__()
        self.provider = (self.PROVIDER or 'anthropic').lower()
        self.client = None
        self.gemini_api_key = None

        if self.provider == 'anthropic':
            api_key = api_key or getattr(settings, 'ANTHROPIC_API_KEY', None)
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY must be set in settings when LLM_PROVIDER=anthropic")
            self.client = Anthropic(api_key=api_key)
        elif self.provider == 'gemini':
            self.gemini_api_key = api_key or getattr(settings, 'GEMINI_API_KEY', None)
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY must be set in settings when LLM_PROVIDER=gemini")
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER '{self.provider}'. Use 'anthropic' or 'gemini'.")

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
                raw_prompt=user_prompt
            )

            # 5. Call Claude API with retry logic
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
                metadata=response_data.get('usage', {})
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
        """Dispatch generation call by configured LLM provider."""
        self._check_circuit_state()

        if self.provider == 'anthropic':
            result = self._call_claude_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                model=self._resolve_model(speed),
                max_retries=self._resolve_retry_count(speed),
                timeout_seconds=self._resolve_timeout_seconds(speed),
            )
            self._record_success()
            return result

        if self.provider == 'gemini':
            result = self._call_gemini_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                model=self._resolve_model(speed),
                max_retries=self._resolve_retry_count(speed),
                timeout_seconds=self._resolve_timeout_seconds(speed),
            )
            self._record_success()
            return result

        raise ServiceError(
            f"Unsupported LLM provider '{self.provider}'",
            code="INVALID_PROVIDER"
        )

    def _check_circuit_state(self) -> None:
        with self._state_lock:
            state = self._provider_state.get(self.provider, {'failures': 0, 'open_until': 0.0})
            if state['open_until'] > time.time():
                retry_after = int(state['open_until'] - time.time())
                raise ServiceError(
                    f"{self.provider} provider temporarily unavailable. Retry in ~{retry_after}s.",
                    code="PROVIDER_UNAVAILABLE",
                    details={'provider': self.provider, 'retry_after_seconds': max(retry_after, 1)}
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

    def _resolve_model(self, speed: str) -> str:
        """Select model by provider and requested speed."""
        if self.provider == 'anthropic':
            return self.FAST_MODEL if speed == 'fast' else self.DEFAULT_MODEL
        if self.provider == 'gemini':
            return self.GEMINI_FAST_MODEL if speed == 'fast' else self.GEMINI_MODEL
        return self.DEFAULT_MODEL

    def _create_post_record(self, topic: str, persona: Persona, raw_prompt: str) -> BlogPost:
        """Create initial BlogPost in GENERATING state"""
        # Generate unique slug
        base_slug = slugify(topic[:50])
        slug = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        blog_post = BlogPost.objects.create(
            title=f"Draft: {topic[:50]}...",
            slug=slug,
            topic_input=topic,
            raw_prompt=raw_prompt,
            persona=persona,
            status=BlogPost.PostStatus.GENERATING
        )
        return blog_post

    def _call_claude_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        model: str,
        max_retries: int,
        timeout_seconds: int,
    ) -> Dict[str, Any]:
        """
        Call Claude API with exponential backoff retry.
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()

                response = self.client.with_options(timeout=timeout_seconds).messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )

                generation_time = time.time() - start_time

                # Extract content and metadata
                content = response.content[0].text if response.content else ""

                return {
                    'content': content,
                    'usage': {
                        'model': model,
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens,
                        'total_tokens': response.usage.input_tokens + response.usage.output_tokens,
                        'generation_time_seconds': round(generation_time, 2),
                        'retry_count': attempt
                    }
                }

            except AnthropicError as e:
                last_error = e
                status_code = getattr(e, 'status_code', None)
                error_message = str(e)

                # Fail fast on non-retriable request errors (e.g. billing/credits, invalid params)
                if status_code and status_code < 500 and status_code != 429:
                    if "credit balance is too low" in error_message.lower():
                        raise ServiceError(
                            "Anthropic billing issue: insufficient API credits. "
                            "Please top up your Anthropic account and try again.",
                            code="BILLING_ERROR",
                            details={'provider': 'anthropic', 'status_code': status_code}
                        )
                    raise ServiceError(
                        f"Anthropic request failed: {error_message}",
                        code="API_REQUEST_ERROR",
                        details={'provider': 'anthropic', 'status_code': status_code}
                    )

                self._logger.warning(
                    f"Claude API call failed (attempt {attempt + 1}/{max_retries + 1}): {error_message}"
                )
                if attempt < max_retries:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))

            except Exception as e:
                last_error = e
                self._logger.error(f"Unexpected error during Claude call: {str(e)}")
                break

        # All retries exhausted
        self._record_failure()
        raise ServiceError(
            "Failed to generate content after retry attempts. Please try again shortly.",
            code="API_ERROR",
            details={'last_error': str(last_error), 'provider': 'anthropic'}
        )

    def _call_gemini_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        model: str,
        max_retries: int,
        timeout_seconds: int,
    ) -> Dict[str, Any]:
        """
        Call Gemini API with retry handling for transient failures.
        """
        last_error = None
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={self.gemini_api_key}"
        )

        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                request = urllib.request.Request(
                    url=url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )

                with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                    response_data = json.loads(response.read().decode('utf-8'))

                generation_time = time.time() - start_time
                candidates = response_data.get('candidates') or []
                parts = (
                    candidates[0].get('content', {}).get('parts', [])
                    if candidates else []
                )
                content = ''.join(part.get('text', '') for part in parts)
                usage = response_data.get('usageMetadata', {})

                return {
                    'content': content,
                    'usage': {
                        'model': model,
                        'input_tokens': usage.get('promptTokenCount', 0),
                        'output_tokens': usage.get('candidatesTokenCount', 0),
                        'total_tokens': usage.get('totalTokenCount', 0),
                        'generation_time_seconds': round(generation_time, 2),
                        'retry_count': attempt,
                        'provider': 'gemini'
                    }
                }

            except urllib.error.HTTPError as e:
                body = e.read().decode('utf-8', errors='ignore')
                last_error = f"HTTP {e.code}: {body}"
                lower_body = body.lower()
                error_message = ""
                error_reason = ""

                try:
                    parsed_error = json.loads(body)
                    error_obj = parsed_error.get('error', {})
                    error_message = error_obj.get('message', '')
                    details = error_obj.get('details') or []
                    for detail in details:
                        if isinstance(detail, dict) and detail.get('reason'):
                            error_reason = detail.get('reason', '')
                            break
                except Exception:
                    pass

                if e.code == 429 and (
                    'resource_exhausted' in lower_body or
                    'exceeded your current quota' in lower_body or
                    'billing' in lower_body
                ):
                    raise ServiceError(
                        "Gemini quota/billing issue: current key has exhausted quota. "
                        "Enable billing or use a key/project with available quota.",
                        code="BILLING_ERROR",
                        details={'provider': 'gemini', 'status_code': e.code}
                    )

                if e.code < 500 and e.code != 429:
                    if error_reason == 'API_KEY_INVALID' or 'api key expired' in lower_body:
                        raise ServiceError(
                            "Gemini API key is invalid or expired. Create/rotate a valid key and retry.",
                            code="AUTH_ERROR",
                            details={
                                'provider': 'gemini',
                                'status_code': e.code,
                                'reason': error_reason or 'API_KEY_INVALID'
                            }
                        )

                    if 'quota' in lower_body or 'billing' in lower_body or 'resource_exhausted' in lower_body:
                        raise ServiceError(
                            "Gemini billing/quota issue: please enable billing or increase quota.",
                            code="BILLING_ERROR",
                            details={'provider': 'gemini', 'status_code': e.code}
                        )
                    raise ServiceError(
                        f"Gemini request failed: {error_message or 'check API key, model name, and payload.'}",
                        code="API_REQUEST_ERROR",
                        details={
                            'provider': 'gemini',
                            'status_code': e.code,
                            'reason': error_reason or None
                        }
                    )

                self._logger.warning(
                    f"Gemini API call failed (attempt {attempt + 1}/{max_retries + 1}): {last_error}"
                )
                if attempt < max_retries:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))

            except Exception as e:
                last_error = str(e)
                self._logger.warning(
                    f"Gemini API call failed (attempt {attempt + 1}/{max_retries + 1}): {last_error}"
                )
                if attempt < max_retries:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))

        self._record_failure()
        raise ServiceError(
            "Failed to generate content after retry attempts. Please try again shortly.",
            code="API_ERROR",
            details={'last_error': str(last_error), 'provider': 'gemini'}
        )

    def _parse_response(self, raw_content: str) -> Dict[str, Any]:
        """
        Parse Claude response to extract:
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
        headings = re.findall(r'^(#{1,3})\s+(.+)$', markdown, re.MULTILINE)
        word_count = len(markdown.split())

        return {
            'word_count': word_count,
            'heading_count': len(headings),
            'reading_time_minutes': max(1, word_count // 200),
            'headings': [{'level': h[0], 'text': h[1]} for h in headings]
        }

    def _update_post_with_content(
        self,
        blog_post: BlogPost,
        content: str,
        sources: List[Dict],
        structure: Dict,
        metadata: Dict
    ) -> None:
        """Update BlogPost with generated content and complete generation"""
        blog_post.generated_content = content
        blog_post.sources = sources
        blog_post.content_structure = structure

        # Update title if extracted
        if structure.get('title'):
            blog_post.title = structure['title'][:300]

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

    def list_blog_posts(
        self,
        status: str = None,
        persona_slug: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """List blog posts with optional filters"""
        queryset = BlogPost.objects.all()

        if status:
            queryset = queryset.filter(status=status)
        if persona_slug:
            queryset = queryset.filter(persona__slug=persona_slug)

        posts = queryset[:limit]

        return [
            {
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'status': p.status,
                'sentiment_score': p.sentiment_score,
                'persona': p.persona.name if p.persona else None,
                'created_at': p.created_at.isoformat()
            }
            for p in posts
        ]

    def delete_blog_post(self, blog_post_id: int) -> bool:
        """Delete a blog post by ID"""
        try:
            post = BlogPost.objects.get(id=blog_post_id)
            post.delete()
            return True
        except BlogPost.DoesNotExist:
            return False

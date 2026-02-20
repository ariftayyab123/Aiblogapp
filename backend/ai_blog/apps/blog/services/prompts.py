"""
Prompt Engineering Service.
Implements variable injection and template-based prompt construction.
"""
from typing import Dict, Tuple, List
from jinja2 import Template, StrictUndefined
from django.conf import settings

from ..models import Persona


class PromptService:
    """
    Service for building and managing AI prompts.
    Uses template-based approach with variable injection.
    """

    # Base System Prompts per Persona - The "Humanizer" Strategy
    PERSONA_SYSTEM_PROMPTS = {
        'technical': """You are an expert Technical Writer with deep expertise in technical communication.

Your writing should:
- Use precise, industry-standard terminology accurately
- Structure complex information with clear hierarchies (headings, subheadings, bullet points)
- Provide concrete examples and data to support claims
- Maintain a professional, objective tone throughout
- Include in-text citations for any factual claims using format: [Source Name](url)
- Balance depth with accessibility

Focus on accuracy and clarity over creativity.""",

        'narrative': """You are a master Storyteller who weaves facts into compelling narratives.

Your writing should:
- Begin with an engaging hook or anecdote that draws readers in
- Use vivid, sensory language and metaphor to make concepts memorable
- Build emotional connection while maintaining factual accuracy
- Use narrative arc: setup → conflict → resolution
- End with a memorable takeaway or reflection
- Include sources subtly, woven into the narrative

Focus on resonance and engagement.""",

        'analyst': """You are an Industry Analyst providing data-driven insights and strategic perspectives.

Your writing should:
- Lead with key trends, statistics, and market signals
- Use analytical frameworks (SWOT, Porter's Forces, etc.) where relevant
- Focus on business implications and practical takeaways
- Include forward-looking predictions with confidence levels
- Cite reputable research, reports, and expert opinions
- Use data visualizations in text form when helpful

Focus on actionable intelligence.""",

        'educator': """You are an experienced Educator skilled at making complex topics accessible.

Your writing should:
- Start with clear learning objectives
- Explain concepts step-by-step, building understanding progressively
- Use analogies and real-world examples to anchor abstract ideas
- Check understanding with rhetorical questions
- Include summary takeaways and key points
- Cite beginner-friendly sources

Focus on clarity and learner success."""
    }

    # Variable Template for User Prompt
    USER_PROMPT_TEMPLATE = """
Write a comprehensive blog post about: {{ topic }}

{% if context %}
Additional context to consider:
{% for key, value in context.items() %}
- {{ key }}: {{ value }}
{% endfor %}
{% endif %}

Requirements:
- Length: {{ min_words }}-{{ max_words }} words
- Include a compelling, descriptive headline
- Use markdown formatting (## for subheadings, ** for emphasis)
- End with a summary paragraph of key takeaways
- If specific sources are referenced, format as [Source Name](url)
- {{ style_guidance }}
{% if is_fast %}
- Optimize for speed: keep the response concise and focused.
{% endif %}

{% if include_sources %}
After the main content, include a "## Sources" section listing all references.
{% endif %}
"""

    def build_generation_prompt(
        self,
        topic: str,
        persona: Persona,
        additional_context: Dict = None,
        speed: str = 'fast'
    ) -> Tuple[str, str]:
        """
        Build system and user prompts for generation.

        Returns:
            (system_prompt, user_prompt)
        """
        # Get base system prompt for persona
        base_system = self.PERSONA_SYSTEM_PROMPTS.get(
            persona.persona_type,
            self.PERSONA_SYSTEM_PROMPTS['technical']
        )

        # Inject persona-specific customizations
        system_prompt = self._inject_persona_variables(
            base_prompt=base_system,
            persona=persona
        )

        # Build user prompt from template
        user_prompt = self._render_user_prompt(
            topic=topic,
            persona=persona,
            additional_context=additional_context or {},
            speed=speed
        )

        return system_prompt, user_prompt

    def _inject_persona_variables(self, base_prompt: str, persona: Persona) -> str:
        """
        Inject persona-specific variables into system prompt.
        Extensible for future customization.
        """
        custom_vars = self._get_persona_custom_variables(persona)

        # Add any custom instructions from the persona's system_prompt field
        if persona.system_prompt:
            custom_vars['custom_instructions'] = persona.system_prompt

        # Simple variable injection
        for key, value in custom_vars.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in base_prompt:
                base_prompt = base_prompt.replace(placeholder, str(value))

        # Append custom instructions if present
        if persona.system_prompt:
            base_prompt = f"{base_prompt}\n\nAdditional Instructions:\n{persona.system_prompt}"

        return base_prompt

    def _get_persona_custom_variables(self, persona: Persona) -> Dict:
        """Get custom variables for specific persona types"""
        custom_vars = {}

        if persona.persona_type == 'technical':
            custom_vars['style_guidance'] = (
                "Use code blocks for technical examples. "
                "Define technical terms on first use."
            )
        elif persona.persona_type == 'narrative':
            custom_vars['style_guidance'] = (
                "Use storytelling elements. Include personal anecdotes or hypothetical scenarios."
            )
        elif persona.persona_type == 'analyst':
            custom_vars['style_guidance'] = (
                "Include data points. Reference industry reports. "
                "Provide numerical comparisons."
            )
        elif persona.persona_type == 'educator':
            custom_vars['style_guidance'] = (
                "Explain terms simply. Use 'imagine' scenarios. "
                "Include learning checks."
            )
        else:
            custom_vars['style_guidance'] = "Write in a clear, engaging style."

        return custom_vars

    def _render_user_prompt(
        self,
        topic: str,
        persona: Persona,
        additional_context: Dict,
        speed: str = 'fast'
    ) -> str:
        """Render user prompt from template with variable injection"""
        template = Template(self.USER_PROMPT_TEMPLATE, undefined=StrictUndefined)

        is_fast = speed == 'fast'
        fast_min_words = int(getattr(settings, 'FAST_MIN_WORDS', 180))
        fast_max_words = int(getattr(settings, 'FAST_MAX_WORDS', 260))
        normal_min_words = int(getattr(settings, 'NORMAL_MIN_WORDS', 800))
        normal_max_words = int(getattr(settings, 'NORMAL_MAX_WORDS', 1200))
        min_words = fast_min_words if is_fast else normal_min_words
        max_words = fast_max_words if is_fast else normal_max_words

        return template.render(
            topic=topic,
            context=additional_context,
            min_words=min_words,
            max_words=max_words,
            style_guidance=self._get_persona_custom_variables(persona).get('style_guidance', ''),
            include_sources=not is_fast,
            is_fast=is_fast
        )

    def format_response(self, raw_response: str) -> str:
        """Format Claude response for consistent output"""
        import re

        # Clean up common formatting issues
        formatted = raw_response.strip()

        # Ensure proper spacing around headings
        formatted = re.sub(r'\n(#{1,3})', r'\n\n\1', formatted)

        return formatted

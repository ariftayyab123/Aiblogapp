from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from ai_blog.apps.blog.services.generation import BlogGenerationService
from ai_blog.apps.blog.services.llm import (
    GeminiProvider,
    LLMProviderError,
    create_llm_provider,
)
from ai_blog.apps.core.services.base import ServiceError


class LLMProviderFactoryTests(SimpleTestCase):
    @override_settings(
        LLM_PROVIDER="gemini",
        GEMINI_API_KEY="test-key",
        GEMINI_MODEL="gemini-normal",
        GEMINI_FAST_MODEL="gemini-fast",
    )
    def test_builds_selected_provider_from_backend_settings(self):
        provider = create_llm_provider()

        self.assertIsInstance(provider, GeminiProvider)
        self.assertEqual(provider.model, "gemini-normal")
        self.assertEqual(provider.fast_model, "gemini-fast")


class BlogGenerationProviderBoundaryTests(SimpleTestCase):
    def test_retries_normalized_transient_provider_failure(self):
        provider = Mock()
        provider.name = "test-provider"
        provider.generate.side_effect = [
            LLMProviderError("temporary upstream error", retryable=True),
            {"content": "# Generated", "usage": {}},
        ]
        service = BlogGenerationService(provider=provider)
        service.MAX_RETRIES = 1

        with patch("ai_blog.apps.blog.services.generation.time.sleep"):
            result = service._call_model_with_retry(
                system_prompt="system",
                user_prompt="user",
                temperature=0.5,
                max_tokens=100,
                speed="normal",
            )

        self.assertEqual(result["content"], "# Generated")
        self.assertEqual(result["usage"]["retry_count"], 1)
        self.assertEqual(provider.generate.call_count, 2)

    def test_provider_specific_failure_is_not_exposed_to_user(self):
        provider = Mock()
        provider.name = "vendor-name"
        provider.generate.side_effect = LLMProviderError(
            "vendor account has no credits",
            code="PROVIDER_BILLING_ERROR",
            retryable=False,
        )
        service = BlogGenerationService(provider=provider)

        with self.assertRaises(ServiceError) as raised:
            service._call_model_with_retry(
                system_prompt="system",
                user_prompt="user",
                temperature=0.5,
                max_tokens=100,
                speed="fast",
            )

        self.assertEqual(raised.exception.code, "PROVIDER_BILLING_ERROR")
        self.assertNotIn("vendor", raised.exception.message.lower())
        self.assertNotIn("credits", raised.exception.message.lower())

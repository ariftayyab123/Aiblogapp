"""Provider adapters for text generation.

The application layer depends on the small ``LLMProvider`` contract below;
vendor SDKs, payloads, and error formats stay inside their adapters.
"""
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, Optional, Protocol

from anthropic import Anthropic, AnthropicError
from django.conf import settings


@dataclass(frozen=True)
class GenerationRequest:
    system_prompt: str
    user_prompt: str
    temperature: float
    max_tokens: int
    speed: str
    timeout_seconds: int


class LLMProviderError(Exception):
    """Normalized provider failure consumed by the application service."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "PROVIDER_ERROR",
        retryable: bool = False,
        status_code: Optional[int] = None,
    ):
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.status_code = status_code


class LLMProvider(Protocol):
    name: str

    def generate(self, request: GenerationRequest) -> Dict:
        """Generate text and return normalized content and usage metadata."""


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str, fast_model: str):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.fast_model = fast_model

    def generate(self, request: GenerationRequest) -> Dict:
        model = self.fast_model if request.speed == "fast" else self.model
        started_at = time.time()

        try:
            response = self.client.with_options(
                timeout=request.timeout_seconds
            ).messages.create(
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=request.system_prompt,
                messages=[{"role": "user", "content": request.user_prompt}],
            )
        except AnthropicError as exc:
            status_code = getattr(exc, "status_code", None)
            message = str(exc)
            lower_message = message.lower()
            is_billing_error = "credit balance is too low" in lower_message
            raise LLMProviderError(
                message,
                code="PROVIDER_BILLING_ERROR" if is_billing_error else "PROVIDER_REQUEST_ERROR",
                retryable=not is_billing_error and (status_code is None or status_code >= 500 or status_code == 429),
                status_code=status_code,
            ) from exc
        except Exception as exc:
            raise LLMProviderError(str(exc), retryable=True) from exc

        content = response.content[0].text if response.content else ""
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        return {
            "content": content,
            "usage": {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "generation_time_seconds": round(time.time() - started_at, 2),
            },
        }


class GeminiProvider:
    name = "gemini"
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: str, model: str, fast_model: str):
        self.api_key = api_key
        self.model = model
        self.fast_model = fast_model

    def generate(self, request: GenerationRequest) -> Dict:
        model = self.fast_model if request.speed == "fast" else self.model
        url = f"{self.endpoint}/{model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": request.user_prompt}]}],
            "systemInstruction": {"parts": [{"text": request.system_prompt}]},
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens,
            },
        }
        started_at = time.time()

        try:
            http_request = urllib.request.Request(
                url=url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(http_request, timeout=request.timeout_seconds) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            lower_body = body.lower()
            is_billing_error = any(
                marker in lower_body
                for marker in ("resource_exhausted", "quota", "billing")
            )
            raise LLMProviderError(
                f"HTTP {exc.code}: {body}",
                code="PROVIDER_BILLING_ERROR" if is_billing_error else "PROVIDER_REQUEST_ERROR",
                retryable=not is_billing_error and (exc.code >= 500 or exc.code == 429),
                status_code=exc.code,
            ) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LLMProviderError(str(exc), retryable=True) from exc
        except Exception as exc:
            raise LLMProviderError(str(exc), retryable=False) from exc

        candidates = response_data.get("candidates") or []
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        content = "".join(part.get("text", "") for part in parts)
        usage = response_data.get("usageMetadata", {})
        return {
            "content": content,
            "usage": {
                "model": model,
                "input_tokens": usage.get("promptTokenCount", 0),
                "output_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0),
                "generation_time_seconds": round(time.time() - started_at, 2),
            },
        }


def create_llm_provider(provider_name: Optional[str] = None, api_key: Optional[str] = None) -> LLMProvider:
    """Build the configured adapter without exposing provider details upstream."""
    name = (provider_name or settings.LLM_PROVIDER).strip().lower()

    if name == "anthropic":
        key = api_key or settings.ANTHROPIC_API_KEY
        if not key:
            raise ValueError("The configured LLM provider API key is missing")
        return AnthropicProvider(
            api_key=key,
            model=settings.ANTHROPIC_MODEL,
            fast_model=settings.ANTHROPIC_FAST_MODEL,
        )

    if name == "gemini":
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("The configured LLM provider API key is missing")
        return GeminiProvider(
            api_key=key,
            model=settings.GEMINI_MODEL,
            fast_model=settings.GEMINI_FAST_MODEL,
        )

    raise ValueError(f"Unsupported LLM provider: {name}")

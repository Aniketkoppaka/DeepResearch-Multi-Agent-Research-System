"""
Unified LiteLLM Gateway — ADR-007 compliant.

This module is the ONLY entry point for all LLM calls in the application.
No application code should import litellm or provider SDKs directly.

Architecture:
  API / Service → LiteLLMGateway → litellm → Provider

Responsibilities:
  - Provider abstraction (OpenAI, Anthropic, Google, Cohere, etc.)
  - Centralized model configuration via Pydantic Settings
  - Timeout enforcement
  - Retry policy with exponential back-off
  - Token / cost tracking foundation
  - Structured error handling and logging
  - Fallback routing on primary model failure
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import litellm
from litellm import acompletion, aembedding
from litellm.exceptions import (

    AuthenticationError,
    BadRequestError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gateway configuration — sourced exclusively from Pydantic Settings
# ---------------------------------------------------------------------------

def _configure_litellm() -> None:
    """Apply global LiteLLM settings from application config."""
    litellm.drop_params = True  # Ignore unsupported provider params silently
    litellm.suppress_debug_info = True  # Silence provider debug output



    # Inject provider API keys — all sourced from environment, never hardcoded
    if settings.OPENAI_API_KEY:
        litellm.openai_key = settings.OPENAI_API_KEY
    if settings.ANTHROPIC_API_KEY:
        litellm.anthropic_key = settings.ANTHROPIC_API_KEY


_configure_litellm()


# ---------------------------------------------------------------------------
# Response / Error types
# ---------------------------------------------------------------------------

@dataclass
class GatewayResponse:
    """Structured response from the LiteLLM gateway."""

    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    cost_usd: Optional[float] = None
    latency_ms: float = 0.0
    fallback_used: bool = False


class GatewayError(Exception):
    """Base class for all gateway errors."""

    def __init__(self, message: str, retryable: bool = False, cause: Optional[Exception] = None):
        super().__init__(message)
        self.retryable = retryable
        self.cause = cause


class GatewayAuthError(GatewayError):
    """Raised when provider authentication fails (missing or invalid API key)."""

    def __init__(self, cause: Optional[Exception] = None):
        super().__init__(
            "LLM provider authentication failed. Check your API key configuration.",
            retryable=False,
            cause=cause,
        )


class GatewayTimeoutError(GatewayError):
    """Raised when the provider call exceeds the configured timeout."""

    def __init__(self, timeout_seconds: int, cause: Optional[Exception] = None):
        super().__init__(
            f"LLM provider call timed out after {timeout_seconds}s.",
            retryable=True,
            cause=cause,
        )


class GatewayRateLimitError(GatewayError):
    """Raised when the provider returns 429 rate limit."""

    def __init__(self, cause: Optional[Exception] = None):
        super().__init__(
            "LLM provider rate limit exceeded. Retry after back-off.",
            retryable=True,
            cause=cause,
        )


class GatewayProviderError(GatewayError):
    """Raised when the provider returns a 5xx or transient failure."""

    def __init__(self, cause: Optional[Exception] = None):
        super().__init__(
            "LLM provider returned a service error.",
            retryable=True,
            cause=cause,
        )


class GatewayConfigError(GatewayError):
    """Raised when the gateway is misconfigured (e.g. missing API key)."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message, retryable=False, cause=cause)


class GatewayBadResponseError(GatewayError):
    """Raised when the provider response is malformed or missing content."""

    def __init__(self, cause: Optional[Exception] = None):
        super().__init__(
            "LLM provider returned a malformed or empty response.",
            retryable=False,
            cause=cause,
        )


# ---------------------------------------------------------------------------
# Core Gateway
# ---------------------------------------------------------------------------

class LiteLLMGateway:
    """
    Unified gateway for all LLM completions.

    Usage:
        gateway = LiteLLMGateway()
        response = await gateway.complete(messages=[{"role": "user", "content": "Hello"}])
    """

    def __init__(
        self,
        model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        self.model = model or settings.LITELLM_DEFAULT_MODEL
        self.fallback_model = fallback_model or settings.LITELLM_FALLBACK_MODEL
        self.timeout_seconds = timeout_seconds or settings.LITELLM_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.LITELLM_MAX_RETRIES
        self.enable_cost_tracking = settings.LITELLM_ENABLE_COST_TRACKING

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> GatewayResponse:
        """
        Issue a chat completion request with retry and fallback.

        Args:
            messages: OpenAI-format message list.
            model: Override the default model for this call only.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            **kwargs: Additional litellm params (passed through).

        Returns:
            GatewayResponse with content, usage, cost, and latency.

        Raises:
            GatewayAuthError, GatewayTimeoutError, GatewayRateLimitError,
            GatewayProviderError, GatewayConfigError, GatewayBadResponseError
        """
        effective_model = model or self.model

        try:
            response = await self._call_with_retry(
                model=effective_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response
        except GatewayError as primary_err:
            if primary_err.retryable and effective_model != self.fallback_model:
                logger.warning(
                    "Primary model %s failed (%s); trying fallback model %s",
                    effective_model,
                    primary_err,
                    self.fallback_model,
                )
                response = await self._call_with_retry(
                    model=self.fallback_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                response.fallback_used = True
                return response
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _call_with_retry(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> GatewayResponse:
        """Call litellm with exponential back-off retry."""
        last_error: Optional[GatewayError] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return await self._single_call(model=model, messages=messages, **kwargs)
            except GatewayError as err:
                last_error = err
                if not err.retryable or attempt == self.max_retries:
                    raise
                backoff = min(2 ** attempt, 32)
                logger.warning(
                    "LiteLLM call attempt %d/%d failed (%s). Retrying in %ds...",
                    attempt,
                    self.max_retries,
                    err,
                    backoff,
                )
                await asyncio.sleep(backoff)

        # Should be unreachable — max_retries exhausted will raise inside loop
        assert last_error is not None
        raise last_error

    async def _single_call(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> GatewayResponse:
        """Make a single litellm acompletion call with timeout and error mapping."""
        start = time.monotonic()
        try:
            response = await asyncio.wait_for(
                acompletion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                ),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            raise GatewayTimeoutError(timeout_seconds=self.timeout_seconds, cause=exc) from exc
        except AuthenticationError as exc:
            raise GatewayAuthError(cause=exc) from exc
        except RateLimitError as exc:
            raise GatewayRateLimitError(cause=exc) from exc
        except (ServiceUnavailableError, Timeout) as exc:
            raise GatewayProviderError(cause=exc) from exc
        except BadRequestError as exc:
            raise GatewayBadResponseError(cause=exc) from exc
        except Exception as exc:
            # Unknown provider error — log and re-raise as provider error
            logger.exception("Unexpected LiteLLM error: %s", exc)
            raise GatewayProviderError(cause=exc) from exc

        latency_ms = (time.monotonic() - start) * 1000

        # Validate response shape
        if not response.choices or not response.choices[0].message:
            raise GatewayBadResponseError()

        content = response.choices[0].message.content or ""
        if not content.strip():
            raise GatewayBadResponseError()

        # Extract usage
        usage: Dict[str, int] = {}
        cost_usd: Optional[float] = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens or 0,
                "completion_tokens": response.usage.completion_tokens or 0,
                "total_tokens": response.usage.total_tokens or 0,
            }

        # Cost tracking (litellm calculates cost automatically when enabled)
        if self.enable_cost_tracking:
            try:
                cost_usd = litellm.completion_cost(
                    completion_response=response
                )

            except Exception:
                cost_usd = None  # Cost lookup failures are non-fatal

        provider = model.split("/")[0] if "/" in model else "openai"

        logger.info(
            "LiteLLM call complete | model=%s provider=%s tokens=%s cost=$%.6f latency=%.0fms",
            model,
            provider,
            usage.get("total_tokens", "unknown"),
            cost_usd or 0.0,
            latency_ms,
        )

        return GatewayResponse(
            content=content,
            model=model,
            provider=provider,
            usage=usage,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
        )

    async def generate_embeddings(
        self,
        input_texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Generate dense vector embeddings with retries and fallback model support.
        """
        if not input_texts:
            return []

        target_model = model or settings.EMBEDDING_MODEL
        fallback_model = settings.EMBEDDING_FALLBACK_MODEL

        try:
            return await self._generate_embeddings_with_retry(
                input_texts=input_texts, model=target_model
            )
        except GatewayAuthError:
            raise
        except GatewayError as exc:
            if fallback_model and fallback_model != target_model:
                logger.warning(
                    "Primary embedding model %s failed (%s). Attempting fallback %s",
                    target_model,
                    exc,
                    fallback_model,
                )
                try:
                    return await self._generate_embeddings_with_retry(
                        input_texts=input_texts, model=fallback_model
                    )
                except Exception as fallback_exc:
                    logger.error(
                        "Fallback embedding model %s failed: %s",
                        fallback_model,
                        fallback_exc,
                    )
                    raise exc from fallback_exc
            raise

    async def _generate_embeddings_with_retry(
        self,
        input_texts: List[str],
        model: str,
    ) -> List[List[float]]:
        attempts = 0
        last_error: Optional[Exception] = None

        while attempts <= self.max_retries:
            try:
                response = await asyncio.wait_for(
                    aembedding(model=model, input=input_texts),
                    timeout=float(self.timeout_seconds),
                )
                embeddings = [item["embedding"] for item in response.data]
                return embeddings
            except (RateLimitError, ServiceUnavailableError) as exc:
                attempts += 1
                last_error = exc
                if attempts > self.max_retries:
                    raise GatewayRateLimitError(cause=exc) if isinstance(
                        exc, RateLimitError
                    ) else GatewayProviderError(cause=exc) from exc
                backoff = (2 ** (attempts - 1)) + (time.monotonic() % 1)
                logger.warning(
                    "Embedding retryable error (%s) on attempt %d/%d. Waiting %.2fs...",
                    type(exc).__name__,
                    attempts,
                    self.max_retries,
                    backoff,
                )
                await asyncio.sleep(backoff)
            except TimeoutError as exc:
                attempts += 1
                last_error = exc
                if attempts > self.max_retries:
                    raise GatewayTimeoutError(
                        f"Embedding call to {model} timed out"
                    ) from exc
                backoff = (2 ** (attempts - 1))
                await asyncio.sleep(backoff)
            except AuthenticationError as exc:
                raise GatewayAuthError(cause=exc) from exc
            except BadRequestError as exc:
                raise GatewayBadResponseError(cause=exc) from exc
            except Exception as exc:
                logger.exception("Unexpected embedding error: %s", exc)
                raise GatewayProviderError(cause=exc) from exc

        raise GatewayProviderError(cause=last_error)


# ---------------------------------------------------------------------------
# Singleton factory — use this in dependency injection
# ---------------------------------------------------------------------------


def get_litellm_gateway(
    model: Optional[str] = None,
    fallback_model: Optional[str] = None,
) -> LiteLLMGateway:
    """FastAPI-compatible factory for the LiteLLM gateway."""
    return LiteLLMGateway(model=model, fallback_model=fallback_model)

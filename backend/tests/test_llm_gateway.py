"""
Unit tests for the Unified LiteLLM Gateway (ADR-007).

All external LLM provider calls are mocked. No real API calls are made.
Tests cover:
  - Successful gateway invocation
  - Model configuration propagation
  - Provider authentication failure
  - Timeout handling
  - Retry behaviour with exponential back-off
  - Fallback model routing
  - Malformed / empty gateway response
  - Missing API key configuration error
  - Rate limit error handling
  - Provider service error
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.llm_gateway import (
    GatewayAuthError,
    GatewayBadResponseError,
    GatewayError,
    GatewayProviderError,
    GatewayRateLimitError,
    GatewayResponse,
    GatewayTimeoutError,
    LiteLLMGateway,
    get_litellm_gateway,
)


# ---------------------------------------------------------------------------
# Helpers & Factories
# ---------------------------------------------------------------------------

def make_litellm_response(content: str = "Hello, world!", model: str = "gpt-4o-mini") -> MagicMock:
    """Build a minimal litellm ModelResponse mock."""
    response = MagicMock()
    response.model = model
    response.choices = [MagicMock()]
    response.choices[0].message = MagicMock()
    response.choices[0].message.content = content
    response.usage = MagicMock()
    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 20
    response.usage.total_tokens = 30
    return response


def make_gateway(**kwargs: Any) -> LiteLLMGateway:
    return LiteLLMGateway(
        model=kwargs.get("model", "gpt-4o-mini"),
        fallback_model=kwargs.get("fallback_model", "gpt-3.5-turbo"),
        timeout_seconds=kwargs.get("timeout_seconds", 30),
        max_retries=kwargs.get("max_retries", 2),
    )


MESSAGES: List[Dict[str, str]] = [{"role": "user", "content": "Hello"}]


# ---------------------------------------------------------------------------
# Test: Successful invocation
# ---------------------------------------------------------------------------

class TestGatewaySuccess:
    @pytest.mark.asyncio
    async def test_successful_completion_returns_gateway_response(self) -> None:
        gateway = make_gateway()
        mock_resp = make_litellm_response("Hi there!")

        with (
            patch("app.core.llm_gateway.acompletion", new=AsyncMock(return_value=mock_resp)),
            patch("app.core.llm_gateway.litellm.completion_cost", return_value=0.00005),
        ):
            result = await gateway.complete(messages=MESSAGES)

        assert isinstance(result, GatewayResponse)
        assert result.content == "Hi there!"
        assert result.model == "gpt-4o-mini"
        assert result.usage["total_tokens"] == 30
        assert result.cost_usd == pytest.approx(0.00005)
        assert result.latency_ms >= 0

        assert result.fallback_used is False

    @pytest.mark.asyncio
    async def test_model_override_used_in_call(self) -> None:
        gateway = make_gateway(model="gpt-4o-mini")
        mock_resp = make_litellm_response("Answer", model="anthropic/claude-3-5-sonnet")

        captured_model: list[str] = []

        async def capture_call(**kwargs: Any) -> Any:
            captured_model.append(kwargs.get("model", ""))
            return mock_resp

        with (
            patch("app.core.llm_gateway.acompletion", new=capture_call),
            patch("app.core.llm_gateway.litellm.completion_cost", return_value=0.0),
        ):
            result = await gateway.complete(messages=MESSAGES, model="anthropic/claude-3-5-sonnet")

        assert captured_model[0] == "anthropic/claude-3-5-sonnet"
        assert result.content == "Answer"


# ---------------------------------------------------------------------------
# Test: Model configuration
# ---------------------------------------------------------------------------

class TestGatewayModelConfiguration:
    def test_default_model_from_settings(self) -> None:
        """Gateway picks up default model from Pydantic Settings."""
        with patch("app.core.llm_gateway.settings") as mock_settings:
            mock_settings.LITELLM_DEFAULT_MODEL = "gpt-4o"
            mock_settings.LITELLM_FALLBACK_MODEL = "gpt-3.5-turbo"
            mock_settings.LITELLM_TIMEOUT_SECONDS = 45
            mock_settings.LITELLM_MAX_RETRIES = 3
            mock_settings.LITELLM_ENABLE_COST_TRACKING = True
            gw = LiteLLMGateway()
            assert gw.model == "gpt-4o"
            assert gw.fallback_model == "gpt-3.5-turbo"
            assert gw.timeout_seconds == 45

    def test_explicit_model_overrides_settings(self) -> None:
        gw = LiteLLMGateway(model="anthropic/claude-3-opus-20240229")
        assert gw.model == "anthropic/claude-3-opus-20240229"

    def test_factory_function_returns_gateway(self) -> None:
        gw = get_litellm_gateway()
        assert isinstance(gw, LiteLLMGateway)

    def test_factory_function_accepts_model_override(self) -> None:
        gw = get_litellm_gateway(model="cohere/command-r")
        assert gw.model == "cohere/command-r"


# ---------------------------------------------------------------------------
# Test: Authentication failure
# ---------------------------------------------------------------------------

class TestGatewayAuthError:
    @pytest.mark.asyncio
    async def test_auth_error_raises_gateway_auth_error(self) -> None:
        from litellm.exceptions import AuthenticationError

        gateway = make_gateway(max_retries=1)
        auth_exc = AuthenticationError(
            message="Invalid API key", llm_provider="openai", model="gpt-4o-mini"
        )

        with patch("app.core.llm_gateway.acompletion", side_effect=auth_exc):
            with pytest.raises(GatewayAuthError) as exc_info:
                await gateway.complete(messages=MESSAGES)

        assert exc_info.value.retryable is False

    @pytest.mark.asyncio
    async def test_auth_error_is_not_retried(self) -> None:
        """AuthenticationError must not be retried (non-retryable)."""
        from litellm.exceptions import AuthenticationError

        gateway = make_gateway(max_retries=3)
        call_count = 0

        async def mock_acompletion(**kwargs: Any) -> Any:
            nonlocal call_count
            call_count += 1
            raise AuthenticationError(
                message="Invalid API key", llm_provider="openai", model="gpt-4o-mini"
            )

        with patch("app.core.llm_gateway.acompletion", new=mock_acompletion):
            with pytest.raises(GatewayAuthError):
                await gateway.complete(messages=MESSAGES)

        # Must only be called once — no retries for auth errors
        assert call_count == 1


# ---------------------------------------------------------------------------
# Test: Timeout handling
# ---------------------------------------------------------------------------

class TestGatewayTimeout:
    @pytest.mark.asyncio
    async def test_timeout_raises_gateway_timeout_error(self) -> None:
        gateway = make_gateway(timeout_seconds=1, max_retries=1)

        async def slow_call(**kwargs: Any) -> Any:
            raise asyncio.TimeoutError()

        with patch("app.core.llm_gateway.asyncio.wait_for", side_effect=asyncio.TimeoutError()):
            with pytest.raises(GatewayTimeoutError) as exc_info:
                await gateway.complete(messages=MESSAGES)

        assert exc_info.value.retryable is True
        assert "1s" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_error_propagated_after_retries_exhausted(self) -> None:
        gateway = make_gateway(max_retries=2, timeout_seconds=1)

        with patch("app.core.llm_gateway.asyncio.sleep", new=AsyncMock()):
            with patch(
                "app.core.llm_gateway.asyncio.wait_for", side_effect=asyncio.TimeoutError()
            ):
                with pytest.raises(GatewayTimeoutError):
                    await gateway.complete(messages=MESSAGES)


# ---------------------------------------------------------------------------
# Test: Retry behaviour
# ---------------------------------------------------------------------------

class TestGatewayRetry:
    @pytest.mark.asyncio
    async def test_retryable_error_retried_up_to_max(self) -> None:
        from litellm.exceptions import ServiceUnavailableError

        gateway = make_gateway(max_retries=3, fallback_model="gpt-4o-mini")
        call_count = 0

        async def flaky(**kwargs: Any) -> Any:
            nonlocal call_count
            call_count += 1
            raise ServiceUnavailableError(
                message="Service down", llm_provider="openai", model="gpt-4o-mini"
            )

        with patch("app.core.llm_gateway.acompletion", new=flaky):
            with patch("app.core.llm_gateway.asyncio.sleep", new=AsyncMock()):
                with pytest.raises(GatewayProviderError):
                    # Also patches fallback — we want to count all attempts
                    await gateway._call_with_retry(model="gpt-4o-mini", messages=MESSAGES)

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_second_attempt(self) -> None:
        from litellm.exceptions import ServiceUnavailableError

        gateway = make_gateway(max_retries=3)
        call_count = 0
        mock_resp = make_litellm_response("Success after retry")

        async def sometimes_fails(**kwargs: Any) -> Any:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ServiceUnavailableError(
                    message="Temporary failure", llm_provider="openai", model="gpt-4o-mini"
                )
            return mock_resp

        with patch("app.core.llm_gateway.acompletion", new=sometimes_fails):
            with patch("app.core.llm_gateway.asyncio.sleep", new=AsyncMock()):
                with patch("app.core.llm_gateway.litellm.completion_cost", return_value=0.0):
                    result = await gateway.complete(messages=MESSAGES)

        assert result.content == "Success after retry"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_fallback_model_used_on_primary_failure(self) -> None:
        from litellm.exceptions import ServiceUnavailableError

        gateway = make_gateway(
            model="gpt-4o",
            fallback_model="gpt-3.5-turbo",
            max_retries=1,
        )
        mock_fallback_resp = make_litellm_response("Fallback response", model="gpt-3.5-turbo")
        called_models: list[str] = []

        async def provider(**kwargs: Any) -> Any:
            called_models.append(kwargs.get("model", ""))
            if kwargs.get("model") == "gpt-4o":
                raise ServiceUnavailableError(
                    message="Service unavailable", llm_provider="openai", model="gpt-4o"
                )
            return mock_fallback_resp

        with patch("app.core.llm_gateway.acompletion", new=provider):
            with patch("app.core.llm_gateway.asyncio.sleep", new=AsyncMock()):
                with patch("app.core.llm_gateway.litellm.completion_cost", return_value=0.0):
                    result = await gateway.complete(messages=MESSAGES)

        assert result.fallback_used is True
        assert result.content == "Fallback response"
        assert "gpt-4o" in called_models
        assert "gpt-3.5-turbo" in called_models


# ---------------------------------------------------------------------------
# Test: Malformed / bad response handling
# ---------------------------------------------------------------------------

class TestGatewayBadResponse:
    @pytest.mark.asyncio
    async def test_empty_content_raises_bad_response_error(self) -> None:
        gateway = make_gateway(max_retries=1)
        mock_resp = make_litellm_response(content="   ")  # whitespace only

        with patch("app.core.llm_gateway.acompletion", new=AsyncMock(return_value=mock_resp)):
            with pytest.raises(GatewayBadResponseError):
                await gateway.complete(messages=MESSAGES)

    @pytest.mark.asyncio
    async def test_no_choices_raises_bad_response_error(self) -> None:
        gateway = make_gateway(max_retries=1)
        mock_resp = MagicMock()
        mock_resp.choices = []
        mock_resp.usage = None

        with patch("app.core.llm_gateway.acompletion", new=AsyncMock(return_value=mock_resp)):
            with pytest.raises(GatewayBadResponseError):
                await gateway.complete(messages=MESSAGES)

    @pytest.mark.asyncio
    async def test_bad_request_raises_bad_response_error(self) -> None:
        from litellm.exceptions import BadRequestError

        gateway = make_gateway(max_retries=1)
        exc = BadRequestError(
            message="Invalid request", llm_provider="openai", model="gpt-4o-mini"
        )
        with patch("app.core.llm_gateway.acompletion", side_effect=exc):
            with pytest.raises(GatewayBadResponseError):
                await gateway.complete(messages=MESSAGES)


# ---------------------------------------------------------------------------
# Test: Missing API key configuration
# ---------------------------------------------------------------------------

class TestGatewayConfig:
    @pytest.mark.asyncio
    async def test_rate_limit_error_is_retryable(self) -> None:
        from litellm.exceptions import RateLimitError

        gateway = make_gateway(max_retries=1)
        exc = RateLimitError(
            message="Rate limit exceeded", llm_provider="openai", model="gpt-4o-mini"
        )
        with patch("app.core.llm_gateway.acompletion", side_effect=exc):
            with pytest.raises(GatewayRateLimitError) as exc_info:
                await gateway._call_with_retry(model="gpt-4o-mini", messages=MESSAGES)

        assert exc_info.value.retryable is True

    def test_gateway_response_dataclass_defaults(self) -> None:
        resp = GatewayResponse(content="test", model="gpt-4o-mini", provider="openai")
        assert resp.usage == {}
        assert resp.cost_usd is None
        assert resp.latency_ms == 0.0
        assert resp.fallback_used is False

    def test_gateway_error_retryable_flag(self) -> None:
        err = GatewayError("test error", retryable=True)
        assert err.retryable is True
        err2 = GatewayError("test error", retryable=False)
        assert err2.retryable is False

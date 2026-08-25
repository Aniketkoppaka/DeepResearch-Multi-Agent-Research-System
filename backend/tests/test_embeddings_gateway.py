"""
Unit tests for LiteLLMGateway dense embeddings generation.
"""

from unittest.mock import AsyncMock, patch
import pytest

from app.core.llm_gateway import (
    LiteLLMGateway,
)
from litellm.exceptions import (
    ServiceUnavailableError,
)


@pytest.mark.asyncio
async def test_generate_embeddings_success():
    gateway = LiteLLMGateway()
    mock_response = AsyncMock()
    mock_response.data = [{"embedding": [0.1, 0.2, 0.3]}, {"embedding": [0.4, 0.5, 0.6]}]

    with patch("app.core.llm_gateway.aembedding", new_callable=AsyncMock) as mock_aembed:
        mock_aembed.return_value = mock_response

        embeddings = await gateway.generate_embeddings(["text 1", "text 2"])
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]
        mock_aembed.assert_called_once()


@pytest.mark.asyncio
async def test_generate_embeddings_empty_list():
    gateway = LiteLLMGateway()
    embeddings = await gateway.generate_embeddings([])
    assert embeddings == []


@pytest.mark.asyncio
async def test_generate_embeddings_fallback_routing():
    gateway = LiteLLMGateway(fallback_model="text-embedding-ada-002")
    mock_response = AsyncMock()
    mock_response.data = [{"embedding": [0.9, 0.8, 0.7]}]

    with patch("app.core.llm_gateway.aembedding", new_callable=AsyncMock) as mock_aembed:
        # First call fails, second call (fallback model) succeeds
        mock_aembed.side_effect = [
            ServiceUnavailableError("Primary failed", response=None, llm_provider="openai", model="text-embedding-3-small"),
            ServiceUnavailableError("Primary failed", response=None, llm_provider="openai", model="text-embedding-3-small"),
            ServiceUnavailableError("Primary failed", response=None, llm_provider="openai", model="text-embedding-3-small"),
            ServiceUnavailableError("Primary failed", response=None, llm_provider="openai", model="text-embedding-3-small"),
            mock_response,
        ]


        embeddings = await gateway.generate_embeddings(["query"])
        assert embeddings == [[0.9, 0.8, 0.7]]

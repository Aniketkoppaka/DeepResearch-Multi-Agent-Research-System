"""
Unit tests for WebSearchEngine and provider fallbacks.
"""

from unittest.mock import AsyncMock
import pytest

from app.services.web_search.base import WebSearchResult
from app.services.web_search.search_service import WebSearchEngine


@pytest.mark.asyncio
async def test_web_search_engine_primary_provider_success():
    mock_primary = AsyncMock()
    mock_primary.search.return_value = [
        WebSearchResult(
            url="https://arxiv.org/abs/2301.00000",
            title="Multi-Agent Reasoning Paper",
            content="Summary of multi-agent cognitive architecture.",
            domain="arxiv.org",
            score=0.95,
        )
    ]
    mock_fallback = AsyncMock()

    engine = WebSearchEngine(
        primary_provider=mock_primary,
        fallback_provider=mock_fallback,
    )

    results = await engine.search("multi-agent systems", max_results=3)
    assert len(results) == 1
    assert results[0].domain == "arxiv.org"
    mock_primary.search.assert_called_once()
    mock_fallback.search.assert_not_called()


@pytest.mark.asyncio
async def test_web_search_engine_fallback_on_primary_failure():
    mock_primary = AsyncMock()
    mock_primary.search.side_effect = RuntimeError("Tavily rate limited")

    mock_fallback = AsyncMock()
    mock_fallback.search.return_value = [
        WebSearchResult(
            url="https://en.wikipedia.org/wiki/Artificial_intelligence",
            title="Artificial Intelligence",
            content="Overview of AI.",
            domain="wikipedia.org",
        )
    ]

    engine = WebSearchEngine(
        primary_provider=mock_primary,
        fallback_provider=mock_fallback,
    )

    results = await engine.search("artificial intelligence")
    assert len(results) == 1
    assert results[0].domain == "wikipedia.org"
    mock_fallback.search.assert_called_once()

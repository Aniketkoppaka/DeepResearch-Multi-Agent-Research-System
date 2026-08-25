"""
Unit tests for SearchAgent query formulation and dual retrieval.
"""

from unittest.mock import AsyncMock
import uuid
import pytest

from app.core.llm_gateway import GatewayResponse, LiteLLMGateway
from app.services.agents.search_agent import SearchAgent
from app.services.agents.state import ResearchPlan
from app.services.retrieval.hybrid_search import HybridSearchService
from app.services.web_search.base import WebSearchResult
from app.services.web_search.search_service import WebSearchEngine


@pytest.mark.asyncio
async def test_search_agent_query_formulation_and_search():
    mock_llm = AsyncMock(spec=LiteLLMGateway)
    mock_llm.complete.return_value = GatewayResponse(
        content='["quantum error correction threshold", "surface code fidelity"]',
        model="gpt-4o-mini",
        provider="openai",
    )

    mock_hybrid = AsyncMock(spec=HybridSearchService)
    mock_hybrid.search.return_value = []

    mock_web = AsyncMock(spec=WebSearchEngine)
    mock_web.search.return_value = [
        WebSearchResult(
            url="https://arxiv.org/abs/2401.000",
            title="Quantum Surface Codes",
            content="Empirical quantum error threshold studies.",
            domain="arxiv.org",
        )
    ]

    agent = SearchAgent(
        hybrid_search=mock_hybrid,
        web_search=mock_web,
        llm_gateway=mock_llm,
    )

    plan = ResearchPlan(
        title="Quantum Error Correction",
        objectives=["Analyze scaling thresholds"],
        research_questions=["What is the physical threshold?"],
        search_strategy={"keywords": ["quantum", "surface code"]},
    )

    queries = await agent.formulate_queries(plan, iteration=1)
    assert len(queries) == 2
    assert "quantum error correction threshold" in queries

    res = await agent.execute_search(
        workspace_id=uuid.uuid4(),
        queries=queries,
    )
    assert len(res.web_results) == 2  # 1 per query executed

"""
Unit and integration tests for ResearchExecutionLoop multi-iteration execution.
"""

from unittest.mock import AsyncMock
import uuid
import pytest
from httpx import AsyncClient

from app.db.models.workspace import PlanStatus, Workspace
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agents.execution_loop import ResearchExecutionLoop
from app.services.agents.fact_extractor import ExtractedClaim, FactExtractorAgent
from app.services.agents.search_agent import SearchAgent, SearchExecutionResult
from app.services.web_search.base import WebSearchResult


@pytest.mark.asyncio
async def test_execution_loop_single_step(db_session):
    workspace_repo = WorkspaceRepository(db_session)
    evidence_repo = EvidenceRepository(db_session)

    mock_search = AsyncMock(spec=SearchAgent)
    mock_search.formulate_queries.return_value = ["ai agent architecture"]
    mock_search.execute_search.return_value = SearchExecutionResult(
        queries_executed=["ai agent architecture"],
        document_chunks=[],
        web_results=[
            WebSearchResult(
                url="https://arxiv.org/abs/2402.000",
                title="Multi-Agent Reasoning Systems",
                content="Multi-agent collaboration outperforms single prompt execution.",
                domain="arxiv.org",
            )
        ],
    )

    mock_extractor = AsyncMock(spec=FactExtractorAgent)
    mock_extractor.extract_claims_from_text.return_value = [
        ExtractedClaim(
            claim_text="Multi-agent collaboration outperforms single prompt execution.",
            claim_type="FINDING",
            confidence_score=0.98,
            entities=["Multi-Agent", "Prompting"],
        )
    ]

    loop = ResearchExecutionLoop(
        workspace_repo=workspace_repo,
        evidence_repo=evidence_repo,
        search_agent=mock_search,
        fact_extractor=mock_extractor,
    )

    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    ws = Workspace(
        id=ws_id,
        user_id=user_id,
        title="Multi-Agent Study",
        plan_status=PlanStatus.APPROVED,
        research_plan={
            "title": "Multi-Agent Study",
            "objectives": ["Analyze architectures"],
            "research_questions": ["Is multi-agent better?"],
        },
    )
    db_session.add(ws)
    await db_session.commit()

    result = await loop.execute_iteration(ws_id, user_id)
    assert result["iteration"] == 1
    assert result["claims_extracted"] == 1

    # Verify node in DB
    nodes = await evidence_repo.list_nodes(ws_id)
    assert len(nodes) == 1
    assert nodes[0].claim_type == "FINDING"


@pytest.mark.asyncio
async def test_execute_api_unauthorized(client: AsyncClient):
    random_ws_id = uuid.uuid4()
    res = await client.post(f"/api/v1/workspaces/{random_ws_id}/execute")
    assert res.status_code in (401, 404)

"""
Integration tests for MetricsService and Metrics REST API.
"""

from unittest.mock import AsyncMock
import uuid
import pytest
from httpx import AsyncClient

from app.db.models.workspace import Workspace
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.evaluations.metrics_service import MetricsService
from app.services.evaluations.ragas_evaluator import EvaluationResult, RagasEvaluator


@pytest.mark.asyncio
async def test_metrics_service_evaluate_and_fetch(db_session):
    metrics_repo = MetricsRepository(db_session)
    workspace_repo = WorkspaceRepository(db_session)
    report_repo = ReportRepository(db_session)
    evidence_repo = EvidenceRepository(db_session)

    mock_eval = AsyncMock(spec=RagasEvaluator)
    mock_eval.evaluate_report.return_value = EvaluationResult(
        faithfulness=0.95,
        answer_relevance=0.92,
        context_precision=0.88,
        details={"status": "verified"},
    )

    service = MetricsService(
        metrics_repo=metrics_repo,
        workspace_repo=workspace_repo,
        report_repo=report_repo,
        evidence_repo=evidence_repo,
        evaluator=mock_eval,
    )

    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    ws = Workspace(
        id=ws_id,
        user_id=user_id,
        title="Evaluation Target WS",
        research_plan={"title": "Target WS", "objectives": ["Obj 1"], "research_questions": ["Q1?"]},
    )
    db_session.add(ws)
    await db_session.commit()

    # 1. Run evaluation
    metric = await service.evaluate_workspace(ws_id, user_id)
    assert metric.faithfulness_score == 0.95
    assert metric.total_tokens > 0
    assert "planner" in metric.agent_token_breakdown

    # 2. Fetch latest metrics
    latest = await service.get_latest_metrics(ws_id, user_id)
    assert latest.id == metric.id


@pytest.mark.asyncio
async def test_metrics_api_unauthorized(client: AsyncClient):
    random_ws_id = uuid.uuid4()
    res = await client.get(f"/api/v1/workspaces/{random_ws_id}/metrics")
    assert res.status_code in (401, 404)

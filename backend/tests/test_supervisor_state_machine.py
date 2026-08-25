"""
Unit and integration tests for Supervisor State Machine & HITL Plan Review.
"""

from unittest.mock import AsyncMock
import uuid
import pytest
from httpx import AsyncClient

from app.db.models.workspace import PlanStatus, Workspace
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agents.planner import PlannerAgent
from app.services.agents.state import ResearchPlan
from app.services.agents.supervisor import SupervisorService


@pytest.mark.asyncio
async def test_supervisor_generate_and_approve_plan(db_session):
    workspace_repo = WorkspaceRepository(db_session)
    mock_planner = AsyncMock(spec=PlannerAgent)

    sample_plan = ResearchPlan(
        title="Autonomous Agent Security",
        objectives=["Analyze prompt injection threats"],
        research_questions=["How to defend against indirect prompt injection?"],
        hypotheses=["Dual LLM verification mitigates injection"],
        search_strategy={"keywords": ["prompt injection"]},
        expected_sources=["Academic"],
        deliverables=["Report"],
    )
    mock_planner.generate_plan.return_value = sample_plan

    supervisor = SupervisorService(
        workspace_repo=workspace_repo,
        planner_agent=mock_planner,
    )

    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    ws = Workspace(
        id=ws_id,
        user_id=user_id,
        title="Agent Security WS",
    )
    db_session.add(ws)
    await db_session.commit()

    # 1. Generate plan -> pending_approval
    plan = await supervisor.generate_workspace_plan(ws_id, user_id)
    assert plan.title == "Autonomous Agent Security"
    refreshed = await workspace_repo.get_by_id_and_user(ws_id, user_id)
    assert refreshed.plan_status == PlanStatus.PENDING_APPROVAL

    # 2. Approve plan -> approved
    approved_ws = await supervisor.review_plan(
        workspace_id=ws_id,
        user_id=user_id,
        approved=True,
    )
    assert approved_ws.plan_status == PlanStatus.APPROVED
    assert approved_ws.execution_state["status"] == "ready_for_execution"


@pytest.mark.asyncio
async def test_plan_api_idor_isolation(client: AsyncClient):
    random_ws_id = uuid.uuid4()
    res = await client.get(f"/api/v1/workspaces/{random_ws_id}/plan")
    assert res.status_code in (401, 404)

import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.deps import (
    get_current_user,
    get_supervisor_service,
    get_workspace_repository,
)
from app.db.models.user import User
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.plan import (
    PlanApprovalRequest,
    PlanGenerateRequest,
    WorkspacePlanResponse,
)
from app.services.agents.state import ResearchPlan
from app.services.agents.supervisor import SupervisorService

router = APIRouter()


@router.get(
    "/{workspace_id}/plan",
    response_model=WorkspacePlanResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspace_plan(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> WorkspacePlanResponse:
    """Retrieve the current research plan and approval status for a workspace."""
    ws = await workspace_repo.get_by_id_and_user(workspace_id, current_user.id)
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )

    plan_obj = (
        ResearchPlan.model_validate(ws.research_plan)
        if ws.research_plan
        else None
    )

    status_str = (
        ws.plan_status.value if hasattr(ws.plan_status, "value") else str(ws.plan_status)
    )

    return WorkspacePlanResponse(
        workspace_id=workspace_id,
        plan_status=status_str,
        research_plan=plan_obj,
        execution_state=ws.execution_state or {},
    )



@router.post(
    "/{workspace_id}/plan/generate",
    response_model=WorkspacePlanResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_workspace_plan(
    workspace_id: uuid.UUID,
    request: PlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    supervisor_service: SupervisorService = Depends(get_supervisor_service),
) -> WorkspacePlanResponse:
    """Trigger the Planner Agent to generate a mode-tailored structured research plan."""
    plan = await supervisor_service.generate_workspace_plan(
        workspace_id=workspace_id,
        user_id=current_user.id,
        user_feedback=request.user_feedback,
    )
    return WorkspacePlanResponse(
        workspace_id=workspace_id,
        plan_status="pending_approval",
        research_plan=plan,
        execution_state={
            "status": "pending_approval",
            "progress_percentage": 10,
        },
    )


@router.post(
    "/{workspace_id}/plan/review",
    response_model=WorkspacePlanResponse,
    status_code=status.HTTP_200_OK,
)
async def review_workspace_plan(
    workspace_id: uuid.UUID,
    request: PlanApprovalRequest,
    current_user: User = Depends(get_current_user),
    supervisor_service: SupervisorService = Depends(get_supervisor_service),
) -> WorkspacePlanResponse:
    """Human-in-the-loop approval or rejection/refinement of the research plan."""
    ws = await supervisor_service.review_plan(
        workspace_id=workspace_id,
        user_id=current_user.id,
        approved=request.approved,
        feedback=request.feedback,
        modified_plan=request.modified_plan,
    )

    plan_obj = (
        ResearchPlan.model_validate(ws.research_plan)
        if ws.research_plan
        else None
    )

    status_str = (
        ws.plan_status.value if hasattr(ws.plan_status, "value") else str(ws.plan_status)
    )

    return WorkspacePlanResponse(
        workspace_id=workspace_id,
        plan_status=status_str,
        research_plan=plan_obj,
        execution_state=ws.execution_state or {},
    )


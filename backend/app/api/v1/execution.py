import uuid
from fastapi import APIRouter, Depends, status

from app.api.v1.deps import (
    get_current_user,
    get_execution_loop,
)
from app.db.models.user import User
from app.schemas.execution import ExecutionStartResponse
from app.services.agents.execution_loop import ResearchExecutionLoop

router = APIRouter()


@router.post(
    "/{workspace_id}/execute",
    response_model=ExecutionStartResponse,
    status_code=status.HTTP_200_OK,
)
async def trigger_research_execution_step(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    execution_loop: ResearchExecutionLoop = Depends(get_execution_loop),
) -> ExecutionStartResponse:
    """
    Trigger a recursive research execution iteration (Search -> Fact Extraction -> EKG Linking).
    """

    result = await execution_loop.execute_iteration(
        workspace_id=workspace_id,
        user_id=current_user.id,
    )
    return ExecutionStartResponse.model_validate(result)

import uuid

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import (
    get_current_user,
    get_metrics_service,
)
from app.db.models.user import User
from app.schemas.metrics import MetricEvaluateRequest, WorkspaceMetricsResponse
from app.services.evaluations.metrics_service import MetricsService

router = APIRouter()


@router.get(
    "/{workspace_id}/metrics",
    response_model=WorkspaceMetricsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspace_metrics(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> WorkspaceMetricsResponse:
    """Retrieve Ragas evaluation metrics, token counts, and cost breakdowns for a workspace."""
    metric = await metrics_service.get_latest_metrics(workspace_id, current_user.id)
    return WorkspaceMetricsResponse.model_validate(metric)


@router.post(
    "/{workspace_id}/evaluate",
    response_model=WorkspaceMetricsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def evaluate_workspace_report(
    workspace_id: uuid.UUID,
    request: MetricEvaluateRequest,
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> WorkspaceMetricsResponse:
    """Trigger a new Ragas grounding evaluation over the synthesized report."""
    metric = await metrics_service.evaluate_workspace(
        workspace_id=workspace_id,
        user_id=current_user.id,
        report_id=request.report_id,
    )
    return WorkspaceMetricsResponse.model_validate(metric)

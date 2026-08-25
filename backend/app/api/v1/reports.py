import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.v1.deps import (
    get_current_user,
    get_report_service,
)
from app.db.models.user import User
from app.schemas.report import ReportGenerateRequest, ReportVersionResponse
from app.services.reports.report_service import ReportService

router = APIRouter()


@router.post(
    "/{workspace_id}/reports/generate",
    response_model=ReportVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_research_report(
    workspace_id: uuid.UUID,
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> ReportVersionResponse:
    """Trigger the Synthesizer Agent to create a new versioned research report."""
    report = await report_service.generate_report(
        workspace_id=workspace_id,
        user_id=current_user.id,
        additional_guidelines=request.additional_guidelines,
    )
    return ReportVersionResponse.model_validate(report)


@router.get(
    "/{workspace_id}/reports",
    response_model=List[ReportVersionResponse],
    status_code=status.HTTP_200_OK,
)
async def list_workspace_reports(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> List[ReportVersionResponse]:
    """List all historical report versions for a workspace."""
    reports = await report_service.list_reports(workspace_id, current_user.id)
    return [ReportVersionResponse.model_validate(r) for r in reports]


@router.get(
    "/{workspace_id}/reports/latest",
    response_model=ReportVersionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_latest_report(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> ReportVersionResponse:
    """Get the latest versioned report with full inline citation resolution."""
    report = await report_service.get_latest_report(workspace_id, current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reports generated yet for this workspace",
        )
    return ReportVersionResponse.model_validate(report)


@router.get(
    "/{workspace_id}/reports/{report_id}/export",
    status_code=status.HTTP_200_OK,
)
async def export_report_file(
    workspace_id: uuid.UUID,
    report_id: uuid.UUID,
    format: str = Query(default="markdown", enum=["markdown", "html"]),
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> Response:
    """Download research report formatted as Markdown or HTML."""
    content, media_type, filename = await report_service.export_report(
        workspace_id=workspace_id,
        report_id=report_id,
        user_id=current_user.id,
        format_type=format,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

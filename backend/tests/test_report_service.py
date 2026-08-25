"""
Integration tests for ReportService, Exporter, and Reports REST API.
"""

from unittest.mock import AsyncMock
import uuid
import pytest
from httpx import AsyncClient

from app.db.models.workspace import Workspace
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agents.synthesizer import SynthesizerAgent
from app.services.reports.report_service import ReportService


@pytest.mark.asyncio
async def test_report_service_generate_and_export(db_session):
    report_repo = ReportRepository(db_session)
    workspace_repo = WorkspaceRepository(db_session)
    evidence_repo = EvidenceRepository(db_session)

    mock_synthesizer = AsyncMock(spec=SynthesizerAgent)
    mock_synthesizer.synthesize_report.return_value = (
        "# Quantum Breakthrough Report\n\nQuantum volume exceeds threshold [1].",
        {"[1]": {"tag": "[1]", "source_title": "Nature Physics", "credibility_score": 0.98}},
    )

    service = ReportService(
        report_repo=report_repo,
        workspace_repo=workspace_repo,
        evidence_repo=evidence_repo,
        synthesizer=mock_synthesizer,
    )

    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    ws = Workspace(
        id=ws_id,
        user_id=user_id,
        title="Quantum Compute Study",
        research_plan={
            "title": "Quantum Compute Study",
            "objectives": ["Analyze qubits"],
            "research_questions": ["What is the physical threshold?"],
        },

    )
    db_session.add(ws)
    await db_session.commit()


    # 1. Generate Report (v1)
    report_v1 = await service.generate_report(ws_id, user_id)
    assert report_v1.version_number == 1
    assert "[1]" in report_v1.citations_json

    # 2. Generate Report (v2)
    report_v2 = await service.generate_report(ws_id, user_id)
    assert report_v2.version_number == 2

    # 3. Export Markdown and HTML
    md_content, md_type, md_file = await service.export_report(ws_id, report_v1.id, user_id, "markdown")
    assert md_type == "text/markdown"
    assert "Quantum Breakthrough Report" in md_content

    html_content, html_type, html_file = await service.export_report(ws_id, report_v1.id, user_id, "html")
    assert html_type == "text/html"
    assert "<!DOCTYPE html>" in html_content


@pytest.mark.asyncio
async def test_reports_api_unauthorized(client: AsyncClient):
    random_ws_id = uuid.uuid4()
    res = await client.get(f"/api/v1/workspaces/{random_ws_id}/reports")
    assert res.status_code in (401, 404)

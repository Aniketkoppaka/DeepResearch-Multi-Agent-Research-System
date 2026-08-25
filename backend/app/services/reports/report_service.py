"""
Report Service coordinating synthesis, version increments, and export downloads.
"""

import logging
from typing import List, Optional
import uuid

from fastapi import HTTPException, status

from app.db.models.report import ReportVersion
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agents.state import ResearchPlan
from app.services.agents.synthesizer import SynthesizerAgent
from app.services.reports.exporter import ReportExporter

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(
        self,
        report_repo: ReportRepository,
        workspace_repo: WorkspaceRepository,
        evidence_repo: EvidenceRepository,
        synthesizer: Optional[SynthesizerAgent] = None,
        exporter: Optional[ReportExporter] = None,
    ) -> None:
        self.report_repo = report_repo
        self.workspace_repo = workspace_repo
        self.evidence_repo = evidence_repo
        self.synthesizer = synthesizer or SynthesizerAgent()
        self.exporter = exporter or ReportExporter()

    async def generate_report(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        additional_guidelines: Optional[str] = None,
    ) -> ReportVersion:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        plan = ResearchPlan.model_validate(ws.research_plan or {})
        sources = await self.evidence_repo.list_sources(workspace_id)
        nodes = await self.evidence_repo.list_nodes(workspace_id)
        contradictions = await self.evidence_repo.get_contradictions(workspace_id)

        # Synthesize markdown and resolve inline citation map
        markdown, citation_map = await self.synthesizer.synthesize_report(
            plan=plan,
            sources=sources,
            nodes=nodes,
            contradictions=contradictions,
            research_mode=ws.research_mode,
            additional_guidelines=additional_guidelines,
        )

        next_version = await self.report_repo.get_next_version_number(workspace_id)
        report = ReportVersion(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            version_number=next_version,
            title=f"Research Report: {ws.title}",
            markdown_content=markdown,
            citations_json=citation_map,
        )
        saved_report = await self.report_repo.create(report)

        # Update workspace execution state
        ws.execution_state = {
            "status": "completed",
            "progress_percentage": 100,
            "latest_report_id": str(saved_report.id),
            "latest_version": next_version,
            "status_messages": [f"Synthesis complete! Version {next_version} generated."],
        }
        await self.workspace_repo.update(ws)

        return saved_report

    async def get_latest_report(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[ReportVersion]:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )
        return await self.report_repo.get_latest_by_workspace(workspace_id)

    async def list_reports(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> List[ReportVersion]:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )
        return await self.report_repo.list_by_workspace(workspace_id)

    async def export_report(
        self,
        workspace_id: uuid.UUID,
        report_id: uuid.UUID,
        user_id: uuid.UUID,
        format_type: str = "markdown",
    ) -> tuple[str, str, str]:
        """
        Returns (file_content, media_type, filename).
        """
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )
        report = await self.report_repo.get_by_id(report_id, workspace_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Report version not found"
            )

        if format_type.lower() == "html":
            content = self.exporter.to_html(
                report.title, report.markdown_content, report.version_number
            )
            return content, "text/html", f"report_v{report.version_number}.html"
        else:
            content = self.exporter.to_markdown(
                report.title, report.markdown_content, report.version_number
            )
            return content, "text/markdown", f"report_v{report.version_number}.md"

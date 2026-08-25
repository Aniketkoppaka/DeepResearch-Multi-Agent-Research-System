"""
Metrics Service coordinating Ragas evaluations and CostTracker data persistence.
"""

import logging
from typing import Optional
import uuid

from fastapi import HTTPException, status

from app.db.models.metrics import WorkspaceMetric
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agents.state import ResearchPlan
from app.services.evaluations.cost_tracker import CostTracker
from app.services.evaluations.ragas_evaluator import RagasEvaluator

logger = logging.getLogger(__name__)


class MetricsService:
    def __init__(
        self,
        metrics_repo: MetricsRepository,
        workspace_repo: WorkspaceRepository,
        report_repo: ReportRepository,
        evidence_repo: EvidenceRepository,
        evaluator: Optional[RagasEvaluator] = None,
    ) -> None:
        self.metrics_repo = metrics_repo
        self.workspace_repo = workspace_repo
        self.report_repo = report_repo
        self.evidence_repo = evidence_repo
        self.evaluator = evaluator or RagasEvaluator()

    async def evaluate_workspace(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        report_id: Optional[uuid.UUID] = None,
    ) -> WorkspaceMetric:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        target_report = (
            await self.report_repo.get_by_id(report_id, workspace_id)
            if report_id
            else await self.report_repo.get_latest_by_workspace(workspace_id)
        )

        plan = ResearchPlan.model_validate(ws.research_plan or {})
        nodes = await self.evidence_repo.list_nodes(workspace_id)
        sources = await self.evidence_repo.list_sources(workspace_id)

        report_md = target_report.markdown_content if target_report else ""
        eval_res = await self.evaluator.evaluate_report(
            plan=plan,
            report_markdown=report_md,
            evidence_nodes=nodes,
        )

        # Calculate token & cost estimates
        total_tokens, total_cost, breakdown = CostTracker.estimate_agent_breakdown(
            num_docs=len(sources),
            num_claims=len(nodes),
            report_length=len(report_md),
        )

        metric = WorkspaceMetric(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            report_id=target_report.id if target_report else None,
            faithfulness_score=eval_res.faithfulness,
            answer_relevance_score=eval_res.answer_relevance,
            context_precision_score=eval_res.context_precision,
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            agent_token_breakdown=breakdown,
            evaluation_details=eval_res.details,
        )

        return await self.metrics_repo.create(metric)

    async def get_latest_metrics(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WorkspaceMetric:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        metric = await self.metrics_repo.get_latest_by_workspace(workspace_id)
        if not metric:
            # Auto-run first evaluation baseline
            return await self.evaluate_workspace(workspace_id, user_id)
        return metric

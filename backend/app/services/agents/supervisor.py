"""
Supervisor State Machine managing Research Workflow & Human-in-the-Loop Plan Review Interrupt.
"""

import logging
from typing import Optional
import uuid

from fastapi import HTTPException, status

from app.db.models.workspace import PlanStatus, Workspace
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agents.planner import PlannerAgent
from app.services.agents.state import ResearchPlan

logger = logging.getLogger(__name__)


class SupervisorService:
    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        planner_agent: Optional[PlannerAgent] = None,
    ) -> None:
        self.workspace_repo = workspace_repo
        self.planner_agent = planner_agent or PlannerAgent()

    async def generate_workspace_plan(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        user_feedback: Optional[str] = None,
    ) -> ResearchPlan:
        """
        Generate structured research plan and transition workspace to PENDING_APPROVAL state.
        """
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        plan = await self.planner_agent.generate_plan(
            title=ws.title,
            description=ws.description,
            research_mode=ws.research_mode,
            user_feedback=user_feedback,
        )

        ws.research_plan = plan.model_dump()
        ws.plan_status = PlanStatus.PENDING_APPROVAL
        ws.execution_state = {
            "status": "pending_approval",
            "current_agent": "planner",
            "progress_percentage": 10,
            "status_messages": ["Research plan generated. Awaiting user approval."],
        }
        await self.workspace_repo.update(ws)
        return plan

    async def review_plan(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        approved: bool,
        feedback: Optional[str] = None,
        modified_plan: Optional[ResearchPlan] = None,
    ) -> Workspace:
        """
        Human-in-the-loop plan review gate.
        If approved -> sets plan_status = APPROVED, execution_state = ready
        If rejected -> sets plan_status = REJECTED, optionally re-plans with feedback
        """
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        if approved:
            if modified_plan:
                ws.research_plan = modified_plan.model_dump()
            ws.plan_status = PlanStatus.APPROVED
            ws.execution_state = {
                "status": "ready_for_execution",
                "current_agent": "supervisor",
                "progress_percentage": 20,
                "status_messages": ["Plan approved by user. Ready for agent execution loop."],
            }
            return await self.workspace_repo.update(ws)
        else:
            if feedback:
                # Re-generate plan incorporating user feedback
                new_plan = await self.planner_agent.generate_plan(
                    title=ws.title,
                    description=ws.description,
                    research_mode=ws.research_mode,
                    user_feedback=feedback,
                )
                ws.research_plan = new_plan.model_dump()
                ws.plan_status = PlanStatus.PENDING_APPROVAL
                ws.execution_state = {
                    "status": "pending_approval",
                    "current_agent": "planner",
                    "progress_percentage": 10,
                    "status_messages": [f"Plan refined based on feedback: {feedback}"],
                }
            else:
                ws.plan_status = PlanStatus.REJECTED
                ws.execution_state = {
                    "status": "rejected",
                    "current_agent": "supervisor",
                    "progress_percentage": 0,
                    "status_messages": ["Plan rejected by user."],
                }
            return await self.workspace_repo.update(ws)

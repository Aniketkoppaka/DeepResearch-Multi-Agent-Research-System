from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field
from app.services.agents.state import ResearchPlan


class PlanGenerateRequest(BaseModel):
    user_feedback: Optional[str] = Field(
        default=None, description="Optional refinement guidelines or feedback"
    )


class PlanApprovalRequest(BaseModel):
    approved: bool = Field(..., description="Whether the plan is approved")
    feedback: Optional[str] = Field(
        default=None, description="Optional feedback if rejected or requesting changes"
    )
    modified_plan: Optional[ResearchPlan] = Field(
        default=None, description="Optional user-edited research plan"
    )


class WorkspacePlanResponse(BaseModel):
    workspace_id: uuid.UUID
    plan_status: str
    research_plan: Optional[ResearchPlan] = None
    execution_state: Dict[str, Any] = Field(default_factory=dict)

from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class WorkspaceMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    report_id: Optional[uuid.UUID] = None
    faithfulness_score: float
    answer_relevance_score: float
    context_precision_score: float
    total_tokens: int
    total_cost_usd: float
    agent_token_breakdown: Dict[str, Any] = Field(default_factory=dict)
    evaluation_details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class MetricEvaluateRequest(BaseModel):
    report_id: Optional[uuid.UUID] = None

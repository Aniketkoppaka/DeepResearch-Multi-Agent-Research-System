from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class CitationDetail(BaseModel):
    tag: str = Field(..., description="Citation marker e.g. [1]")
    node_id: Optional[uuid.UUID] = None
    source_id: Optional[uuid.UUID] = None
    source_title: str
    source_url: Optional[str] = None
    credibility_score: float = 0.5
    quote_snippet: Optional[str] = None
    claim_type: Optional[str] = None


class ReportVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    version_number: int
    title: str
    markdown_content: str
    citations_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ReportGenerateRequest(BaseModel):
    additional_guidelines: Optional[str] = Field(
        default=None, description="Optional custom synthesis guidelines"
    )

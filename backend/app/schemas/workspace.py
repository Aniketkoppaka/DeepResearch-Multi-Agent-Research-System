import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.workspace import ResearchMode, WorkspaceStatus


class WorkspaceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    research_mode: ResearchMode = ResearchMode.DEEP


class WorkspaceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    research_mode: Optional[ResearchMode] = None
    status: Optional[WorkspaceStatus] = None


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str] = None
    research_mode: ResearchMode
    status: WorkspaceStatus
    created_at: datetime
    updated_at: datetime

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    workspace_id: uuid.UUID
    chunk_index: int
    content: str
    estimated_tokens: int
    section_heading: Optional[str] = None
    page_number: Optional[int] = None
    metadata_json: Dict[str, Any]
    created_at: datetime


class IngestionTriggerResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    message: str

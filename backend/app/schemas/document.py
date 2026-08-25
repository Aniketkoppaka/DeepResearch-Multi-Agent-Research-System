import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    filename: str
    mime_type: str
    file_size: int
    storage_key: str
    status: str
    error_message: Optional[str] = None
    chunk_count: int = 0
    created_at: datetime

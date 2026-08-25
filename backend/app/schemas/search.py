import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    document_ids: Optional[List[uuid.UUID]] = Field(
        default=None, description="Optional document filter list"
    )
    limit: int = Field(default=10, ge=1, le=50, description="Max results to return")


class SearchResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chunk_id: uuid.UUID
    document_id: uuid.UUID
    workspace_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    section_heading: Optional[str] = None
    page_number: Optional[int] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class SearchQueryResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultResponse]

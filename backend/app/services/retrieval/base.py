"""
Data classes and interfaces for retrieval and search engine.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class SparseVector:
    """Sparse vector representation containing term indices and values."""

    indices: List[int]
    values: List[float]


@dataclass
class SearchResultItem:
    """Individual retrieval result from dense, sparse, or hybrid search."""

    chunk_id: uuid.UUID
    document_id: uuid.UUID
    workspace_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    section_heading: Optional[str] = None
    page_number: Optional[int] = None
    metadata_json: Dict[str, Any] = field(default_factory=dict)

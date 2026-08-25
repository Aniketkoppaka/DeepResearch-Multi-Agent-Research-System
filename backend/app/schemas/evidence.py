"""
Canonical Pydantic domain models and schemas for Evidence Knowledge Graph (EKG).
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field


class ClaimType(str, Enum):
    FACT = "FACT"
    STATISTIC = "STATISTIC"
    FINDING = "FINDING"
    HYPOTHESIS = "HYPOTHESIS"
    OPINION = "OPINION"


class RelationshipType(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    ELABORATES = "ELABORATES"
    RELATED_TO = "RELATED_TO"


class EvidenceSourceCreate(BaseModel):
    url: Optional[str] = None
    title: str = Field(..., min_length=1)
    domain: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[datetime] = None


class EvidenceSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    url: Optional[str] = None
    title: str
    domain: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    credibility_score: float
    credibility_breakdown: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class EvidenceNodeCreate(BaseModel):
    source_id: uuid.UUID
    claim_text: str = Field(..., min_length=1)
    claim_type: ClaimType = ClaimType.FACT
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    extracted_by_agent: str = Field(default="system")
    supporting_reasoning: Optional[str] = None
    entities: List[str] = Field(default_factory=list)


class EvidenceNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    source_id: uuid.UUID
    claim_text: str
    claim_type: str
    confidence_score: float
    extracted_by_agent: str
    supporting_reasoning: Optional[str] = None
    entities: List[str] = Field(default_factory=list)
    created_at: datetime


class EvidenceEdgeCreate(BaseModel):
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    relationship_type: RelationshipType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class EvidenceEdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    relationship_type: str
    confidence: float
    reasoning: Optional[str] = None
    created_at: datetime


class EvidenceGraphResponse(BaseModel):
    workspace_id: uuid.UUID
    sources: List[EvidenceSourceResponse]
    nodes: List[EvidenceNodeResponse]
    edges: List[EvidenceEdgeResponse]
    total_nodes: int
    total_edges: int

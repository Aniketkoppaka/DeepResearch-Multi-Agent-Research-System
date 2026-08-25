"""
SQLAlchemy ORM models for the Relational Evidence Knowledge Graph (EKG).
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    UUID as SQLUUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.user import Base

if TYPE_CHECKING:
    from app.db.models.workspace import Workspace


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    credibility_score: Mapped[float] = mapped_column(
        Float, server_default="0.5", nullable=False
    )
    credibility_breakdown: Mapped[Dict[str, Any]] = mapped_column(
        JSON, server_default="{}", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    workspace: Mapped["Workspace"] = relationship("Workspace")
    nodes: Mapped[List["EvidenceNode"]] = relationship(
        "EvidenceNode",
        back_populates="source",
        cascade="all, delete-orphan",
    )


class EvidenceNode(Base):
    __tablename__ = "evidence_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("evidence_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    extracted_by_agent: Mapped[str] = mapped_column(String(64), nullable=False)
    supporting_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entities: Mapped[List[str]] = mapped_column(
        JSON, server_default="[]", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    source: Mapped["EvidenceSource"] = relationship(
        "EvidenceSource", back_populates="nodes"
    )
    workspace: Mapped["Workspace"] = relationship("Workspace")


class EvidenceEdge(Base):
    __tablename__ = "evidence_edges"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("evidence_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("evidence_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(
        Float, server_default="1.0", nullable=False
    )
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    source_node: Mapped["EvidenceNode"] = relationship(
        "EvidenceNode", foreign_keys=[source_node_id]
    )
    target_node: Mapped["EvidenceNode"] = relationship(
        "EvidenceNode", foreign_keys=[target_node_id]
    )
    workspace: Mapped["Workspace"] = relationship("Workspace")

    __table_args__ = (
        UniqueConstraint(
            "source_node_id",
            "target_node_id",
            "relationship_type",
            name="uq_evidence_edge",
        ),
    )

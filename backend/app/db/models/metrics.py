"""
SQLAlchemy ORM model for WorkspaceMetric.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional
import uuid

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    UUID as SQLUUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.user import Base

if TYPE_CHECKING:
    from app.db.models.report import ReportVersion
    from app.db.models.workspace import Workspace


class WorkspaceMetric(Base):
    __tablename__ = "workspace_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("report_versions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    faithfulness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    answer_relevance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    context_precision_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    agent_token_breakdown: Mapped[Dict[str, Any]] = mapped_column(
        JSON, server_default="{}", nullable=False
    )
    evaluation_details: Mapped[Dict[str, Any]] = mapped_column(
        JSON, server_default="{}", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    workspace: Mapped["Workspace"] = relationship("Workspace")
    report: Mapped[Optional["ReportVersion"]] = relationship("ReportVersion")

"""
SQLAlchemy ORM model for ReportVersion.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict
import uuid

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    UUID as SQLUUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.user import Base

if TYPE_CHECKING:
    from app.db.models.workspace import Workspace


class ReportVersion(Base):
    __tablename__ = "report_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    citations_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON, server_default="{}", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    workspace: Mapped["Workspace"] = relationship("Workspace")

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "version_number",
            name="uq_workspace_report_version",
        ),
    )

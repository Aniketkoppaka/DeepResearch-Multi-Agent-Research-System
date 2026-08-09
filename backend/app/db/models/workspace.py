import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Enum, ForeignKey, String, Text, DateTime, UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.user import Base, User

if TYPE_CHECKING:
    from app.db.models.document import Document


class ResearchMode(str, enum.Enum):
    QUICK = "Quick"
    DEEP = "Deep"
    ACADEMIC = "Academic"


class WorkspaceStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    research_mode: Mapped[ResearchMode] = mapped_column(
        Enum(ResearchMode, native_enum=False),
        default=ResearchMode.DEEP,
        nullable=False,
    )
    status: Mapped[WorkspaceStatus] = mapped_column(
        Enum(WorkspaceStatus, native_enum=False),
        default=WorkspaceStatus.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped[User] = relationship("User")
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="workspace", cascade="all, delete-orphan"
    )

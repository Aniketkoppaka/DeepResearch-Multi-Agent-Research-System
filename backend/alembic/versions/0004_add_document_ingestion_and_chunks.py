"""add_document_ingestion_and_chunks

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-09 19:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add ingestion status, error_message, and chunk_count to documents table
    op.add_column(
        "documents",
        sa.Column(
            "status",
            sa.String(32),
            server_default="uploaded",
            nullable=False,
        ),
    )
    op.create_index("ix_documents_status", "documents", ["status"])
    op.add_column("documents", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column(
        "documents",
        sa.Column("chunk_count", sa.Integer(), server_default="0", nullable=False),
    )

    # 2. Create document_chunks table
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "document_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "workspace_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("estimated_tokens", sa.Integer(), nullable=False),
        sa.Column("section_heading", sa.String(255), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column(
            "metadata_json",
            sa.JSON(),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "document_id", "chunk_index", name="uq_document_chunk_index"
        ),
    )
    op.create_index(
        "ix_document_chunks_workspace_document",
        "document_chunks",
        ["workspace_id", "document_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_document_chunks_workspace_document", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_column("documents", "chunk_count")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "status")

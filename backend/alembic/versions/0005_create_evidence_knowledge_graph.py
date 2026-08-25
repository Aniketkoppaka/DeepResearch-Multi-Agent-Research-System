"""create_evidence_knowledge_graph

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-25 23:45:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create evidence_sources table
    op.create_table(
        "evidence_sources",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workspace_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("publication_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "credibility_score",
            sa.Float(),
            server_default="0.5",
            nullable=False,
        ),
        sa.Column(
            "credibility_breakdown",
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
    )

    # 2. Create evidence_nodes (Claims, Facts, Findings, Hypotheses) table
    op.create_table(
        "evidence_nodes",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workspace_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "source_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("evidence_sources.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("claim_type", sa.String(32), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("extracted_by_agent", sa.String(64), nullable=False),
        sa.Column("supporting_reasoning", sa.Text(), nullable=True),
        sa.Column("entities", sa.JSON(), server_default="[]", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # 3. Create evidence_edges (Relational EKG Links) table
    op.create_table(
        "evidence_edges",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workspace_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "source_node_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("evidence_nodes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "target_node_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("evidence_nodes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("relationship_type", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "source_node_id",
            "target_node_id",
            "relationship_type",
            name="uq_evidence_edge",
        ),
    )


def downgrade() -> None:
    op.drop_table("evidence_edges")
    op.drop_table("evidence_nodes")
    op.drop_table("evidence_sources")

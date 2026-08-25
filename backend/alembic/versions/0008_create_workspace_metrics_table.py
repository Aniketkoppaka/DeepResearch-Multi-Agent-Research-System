"""create_workspace_metrics_table

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-26 00:30:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspace_metrics",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workspace_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "report_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("report_versions.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("faithfulness_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("answer_relevance_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("context_precision_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_cost_usd", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "agent_token_breakdown",
            sa.JSON(),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "evaluation_details",
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


def downgrade() -> None:
    op.drop_table("workspace_metrics")

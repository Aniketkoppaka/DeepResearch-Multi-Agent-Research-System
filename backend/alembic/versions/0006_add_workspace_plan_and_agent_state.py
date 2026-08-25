"""add_workspace_plan_and_agent_state

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-26 00:05:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add research_plan, plan_status, and execution_state to workspaces
    op.add_column(
        "workspaces",
        sa.Column("research_plan", sa.JSON(), nullable=True),
    )
    op.add_column(
        "workspaces",
        sa.Column(
            "plan_status",
            sa.String(32),
            server_default="draft",
            nullable=False,
        ),
    )
    op.add_column(
        "workspaces",
        sa.Column(
            "execution_state",
            sa.JSON(),
            server_default="{}",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("workspaces", "execution_state")
    op.drop_column("workspaces", "plan_status")
    op.drop_column("workspaces", "research_plan")

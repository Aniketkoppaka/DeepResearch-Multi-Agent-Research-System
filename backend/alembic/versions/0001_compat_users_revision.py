"""compatibility bridge for revision 0001 alias

Revision ID: 0001
Revises: 0001_create_users_table
Create Date: 2026-08-09 18:55:00.000000
"""

from typing import Sequence, Union

revision: str = "0001"
down_revision: Union[str, None] = "0001_create_users_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No-op bridge migration to resolve historical down_revision = "0001" in 0002
    pass


def downgrade() -> None:
    # No-op bridge migration
    pass

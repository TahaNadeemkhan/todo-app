"""add completed_at column

Revision ID: add_completed_at
Revises: event_log_table
Create Date: 2026-01-23 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_completed_at'
down_revision: Union[str, None] = 'event_log_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('tasks')]

    if 'completed_at' not in columns:
        op.add_column('tasks', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'completed_at')

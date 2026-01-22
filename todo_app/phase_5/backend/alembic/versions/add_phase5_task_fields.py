"""add phase 5 task fields

Revision ID: phase5_task_fields
Revises: fix_due_date_timezone
Create Date: 2026-01-05 16:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'phase5_task_fields'
down_revision: Union[str, None] = 'fix_due_date_timezone'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add priority column (enum: high, medium, low)
    op.add_column('tasks', sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'))

    # Add tags column (JSON array)
    op.add_column('tasks', sa.Column('tags', postgresql.JSONB(), nullable=False, server_default='[]'))

    # Add due_at column (timestamp with timezone)
    op.add_column('tasks', sa.Column('due_at', sa.DateTime(timezone=True), nullable=True))

    # Add recurrence_id column (foreign key to task_recurrences table)
    op.add_column('tasks', sa.Column('recurrence_id', sa.String(length=36), nullable=True))

    # Create indexes for better query performance
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_due_at', 'tasks', ['due_at'])
    op.create_index('ix_tasks_user_id_due_at', 'tasks', ['user_id', 'due_at'])
    op.create_index('ix_tasks_user_id_priority', 'tasks', ['user_id', 'priority'])

    # Create GIN index for tags JSON column for faster array searches
    op.execute('CREATE INDEX ix_tasks_tags ON tasks USING GIN (tags)')


def downgrade() -> None:
    # Drop indexes
    op.execute('DROP INDEX IF EXISTS ix_tasks_tags')
    op.drop_index('ix_tasks_user_id_priority', table_name='tasks')
    op.drop_index('ix_tasks_user_id_due_at', table_name='tasks')
    op.drop_index('ix_tasks_due_at', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')

    # Drop columns
    op.drop_column('tasks', 'recurrence_id')
    op.drop_column('tasks', 'due_at')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')

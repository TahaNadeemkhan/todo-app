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
down_revision: Union[str, None] = 'fix_due_date_tz'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('tasks')]
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('tasks')]

    # Add priority column (enum: high, medium, low)
    if 'priority' not in columns:
        op.add_column('tasks', sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'))

    # Add tags column (JSON array)
    if 'tags' not in columns:
        op.add_column('tasks', sa.Column('tags', postgresql.JSONB(), nullable=False, server_default='[]'))

    # Add due_at column (timestamp with timezone)
    if 'due_at' not in columns:
        op.add_column('tasks', sa.Column('due_at', sa.DateTime(timezone=True), nullable=True))

    # Add recurrence_id column (foreign key to task_recurrences table)
    if 'recurrence_id' not in columns:
        op.add_column('tasks', sa.Column('recurrence_id', sa.String(length=36), nullable=True))
        
    # Add completed_at column (timestamp with timezone)
    if 'completed_at' not in columns:
        op.add_column('tasks', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    # Create indexes for better query performance
    if 'ix_tasks_priority' not in existing_indexes:
        op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    if 'ix_tasks_due_at' not in existing_indexes:
        op.create_index('ix_tasks_due_at', 'tasks', ['due_at'])
    if 'ix_tasks_user_id_due_at' not in existing_indexes:
        op.create_index('ix_tasks_user_id_due_at', 'tasks', ['user_id', 'due_at'])
    if 'ix_tasks_user_id_priority' not in existing_indexes:
        op.create_index('ix_tasks_user_id_priority', 'tasks', ['user_id', 'priority'])

    # Create GIN index for tags JSON column for faster array searches
    # Check if index exists via raw SQL or inspector (inspector might miss custom index types or names depending on driver)
    # The name is 'ix_tasks_tags'.
    if 'ix_tasks_tags' not in existing_indexes:
        op.execute('CREATE INDEX IF NOT EXISTS ix_tasks_tags ON tasks USING GIN (tags)')


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

"""create task_recurrences table

Revision ID: task_recurrences_table
Revises: phase5_task_fields
Create Date: 2026-01-05 16:35:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'task_recurrences_table'
down_revision: Union[str, None] = 'phase5_task_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task_recurrences table
    op.create_table(
        'task_recurrences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=36), nullable=False),
        sa.Column('pattern', sa.String(length=20), nullable=False),  # daily, weekly, monthly
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('days_of_week', postgresql.JSONB(), nullable=True),  # [0,1,2,3,4,5,6] for weekly
        sa.Column('day_of_month', sa.Integer(), nullable=True),  # 1-31 for monthly
        sa.Column('next_due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_task_recurrences_task_id', 'task_recurrences', ['task_id'])
    op.create_index('ix_task_recurrences_active', 'task_recurrences', ['active'])
    op.create_index('ix_task_recurrences_next_due_at', 'task_recurrences', ['next_due_at'])

    # Add foreign key constraint to tasks table
    op.create_foreign_key(
        'fk_tasks_recurrence_id',
        'tasks', 'task_recurrences',
        ['recurrence_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_tasks_recurrence_id', 'tasks', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_task_recurrences_next_due_at', table_name='task_recurrences')
    op.drop_index('ix_task_recurrences_active', table_name='task_recurrences')
    op.drop_index('ix_task_recurrences_task_id', table_name='task_recurrences')

    # Drop table
    op.drop_table('task_recurrences')

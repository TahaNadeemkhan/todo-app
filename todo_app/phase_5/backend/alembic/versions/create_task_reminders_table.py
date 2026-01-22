"""create task_reminders table

Revision ID: task_reminders_table
Revises: task_recurrences_table
Create Date: 2026-01-05 16:36:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'task_reminders_table'
down_revision: Union[str, None] = 'task_recurrences_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task_reminders table
    op.create_table(
        'task_reminders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('remind_before', sa.String(length=20), nullable=False),  # ISO 8601 duration (PT1H, P1D, P1W)
        sa.Column('channels', postgresql.JSONB(), nullable=False),  # ["email", "push"]
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_task_reminders_task_id', 'task_reminders', ['task_id'])
    op.create_index('ix_task_reminders_user_id', 'task_reminders', ['user_id'])
    op.create_index('ix_task_reminders_sent_at', 'task_reminders', ['sent_at'])

    # Add foreign key constraint to tasks table
    op.create_foreign_key(
        'fk_task_reminders_task_id',
        'task_reminders', 'tasks',
        ['task_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_task_reminders_task_id', 'task_reminders', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_task_reminders_sent_at', table_name='task_reminders')
    op.drop_index('ix_task_reminders_user_id', table_name='task_reminders')
    op.drop_index('ix_task_reminders_task_id', table_name='task_reminders')

    # Drop table
    op.drop_table('task_reminders')

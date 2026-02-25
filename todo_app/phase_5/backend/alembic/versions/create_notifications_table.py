"""create notifications table

Revision ID: notifications_table
Revises: task_reminders_table
Create Date: 2026-01-05 16:37:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'notifications_table'
down_revision: Union[str, None] = 'task_reminders_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=36), nullable=True),
        sa.Column('channel', sa.String(length=10), nullable=False),  # email, push
        sa.Column('status', sa.String(length=10), nullable=False),  # pending, sent, failed
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_task_id', 'notifications', ['task_id'])
    op.create_index('ix_notifications_status', 'notifications', ['status'])
    op.create_index('ix_notifications_channel', 'notifications', ['channel'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])

    # Add foreign key constraint to tasks table (optional, can be null)
    op.create_foreign_key(
        'fk_notifications_task_id',
        'notifications', 'tasks',
        ['task_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_notifications_task_id', 'notifications', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_channel', table_name='notifications')
    op.drop_index('ix_notifications_status', table_name='notifications')
    op.drop_index('ix_notifications_task_id', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')

    # Drop table
    op.drop_table('notifications')

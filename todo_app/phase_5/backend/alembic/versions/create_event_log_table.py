"""create event_log table for idempotency

Revision ID: event_log_table
Revises: notifications_table
Create Date: 2026-01-05 16:40:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'event_log_table'
down_revision: Union[str, None] = 'notifications_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create event_log table for idempotency tracking
    op.create_table(
        'event_log',
        sa.Column('event_id', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('consumer_service', sa.String(length=50), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('data', sa.String(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='processed'),
        sa.Column('error', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('event_id')
    )

    # Create indexes for efficient queries
    op.create_index('ix_event_log_event_type', 'event_log', ['event_type'])
    op.create_index('ix_event_log_consumer_service', 'event_log', ['consumer_service'])
    op.create_index('ix_event_log_processed_at', 'event_log', ['processed_at'])
    op.create_index('ix_event_log_expires_at', 'event_log', ['expires_at'])
    op.create_index('ix_event_log_status', 'event_log', ['status'])

    # Create composite index for common query pattern
    op.create_index('ix_event_log_consumer_event_type', 'event_log', ['consumer_service', 'event_type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_event_log_consumer_event_type', table_name='event_log')
    op.drop_index('ix_event_log_status', table_name='event_log')
    op.drop_index('ix_event_log_expires_at', table_name='event_log')
    op.drop_index('ix_event_log_processed_at', table_name='event_log')
    op.drop_index('ix_event_log_consumer_service', table_name='event_log')
    op.drop_index('ix_event_log_event_type', table_name='event_log')

    # Drop table
    op.drop_table('event_log')

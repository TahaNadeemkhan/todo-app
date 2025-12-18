"""add conversation and message tables

Revision ID: 2f396b4cc71c
Revises: 
Create Date: 2025-12-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2f396b4cc71c'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create message_role enum
    sa.Enum('user', 'assistant', name='messagerole').create(op.get_bind(), checkfirst=True)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('char_length(content) > 0', name='content_not_empty'),
        sa.CheckConstraint('char_length(content) <= 2000', name='content_max_length'),
    )
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])

    # Trigger for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_conversations_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER conversations_updated_at
        BEFORE UPDATE ON conversations
        FOR EACH ROW
        EXECUTE FUNCTION update_conversations_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS conversations_updated_at ON conversations")
    op.execute("DROP FUNCTION IF EXISTS update_conversations_updated_at()")
    op.drop_table('messages')
    op.drop_table('conversations')
    sa.Enum('user', 'assistant', name='messagerole').drop(op.get_bind(), checkfirst=True)
"""fix due_date timezone column

Revision ID: fix_due_date_tz
Revises: 2f396b4cc71c
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_due_date_tz'
down_revision: Union[str, None] = '2f396b4cc71c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change due_date from TIMESTAMP WITHOUT TIME ZONE to TIMESTAMP WITH TIME ZONE
    # First, drop the NOT NULL constraint to allow NULL during migration
    op.execute('ALTER TABLE tasks ALTER COLUMN due_date DROP NOT NULL')

    # Change column type to TIMESTAMP WITH TIME ZONE
    op.alter_column(
        'tasks',
        'due_date',
        existing_type=sa.TIMESTAMP(timezone=False),
        type_=sa.TIMESTAMP(timezone=True),
        nullable=True
    )


def downgrade() -> None:
    # Revert back to TIMESTAMP WITHOUT TIME ZONE
    op.alter_column(
        'tasks',
        'due_date',
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=sa.TIMESTAMP(timezone=False),
        nullable=True
    )

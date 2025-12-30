"""add_uppercase_tool_to_message_enum

Revision ID: 5b0264a3470f
Revises: 0b2be14c6077
Create Date: 2025-12-26 09:56:41.436424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b0264a3470f'
down_revision: Union[str, Sequence[str], None] = '0b2be14c6077'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add 'TOOL' (uppercase) to MessageRole enum to match existing pattern."""
    # PostgreSQL: Add new value to existing enum type
    # The existing enum has 'USER' and 'ASSISTANT' in uppercase
    # We previously added 'tool' in lowercase by mistake
    # Now adding 'TOOL' in uppercase to match the pattern
    op.execute("ALTER TYPE messagerole ADD VALUE IF NOT EXISTS 'TOOL'")


def downgrade() -> None:
    """
    Downgrade schema.

    Note: PostgreSQL does not support removing values from enum types.
    This downgrade is a no-op.
    """
    pass

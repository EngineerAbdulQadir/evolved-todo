"""add_tool_role_to_message_enum

Revision ID: 0b2be14c6077
Revises: 8808489c43b3
Create Date: 2025-12-26 09:35:40.638410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b2be14c6077'
down_revision: Union[str, Sequence[str], None] = '8808489c43b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add 'tool' role to MessageRole enum for agent conversation history."""
    # PostgreSQL: Add new value to existing enum type
    # Note: This is safe because we're only adding a value, not removing
    op.execute("ALTER TYPE messagerole ADD VALUE IF NOT EXISTS 'tool'")


def downgrade() -> None:
    """
    Downgrade schema.

    Note: PostgreSQL does not support removing values from enum types.
    To properly downgrade, you would need to:
    1. Create a new enum type without 'tool'
    2. Update all columns to use the new type
    3. Drop the old type
    4. Rename the new type

    For simplicity, this downgrade is a no-op since removing enum values
    is complex and the 'tool' value doesn't break backward compatibility.
    """
    pass

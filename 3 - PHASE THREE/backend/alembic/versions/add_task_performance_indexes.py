"""Add task performance indexes

Revision ID: add_task_indexes
Revises: 97fb7e90c831
Create Date: 2025-12-14

Description:
    Add database indexes for performance optimization (T224).

    Indexes added:
    - user_id: Already created with foreign key
    - created_at: For sorting and filtering by creation date
    - due_date: For filtering tasks by due date range
    - is_complete + user_id: For filtering active/completed tasks
    - priority + user_id: For filtering by priority

    These indexes optimize the most common query patterns:
    - Get all tasks for a user (user_id)
    - Sort tasks by creation date (created_at)
    - Filter by due date range (due_date)
    - Filter by completion status (is_complete + user_id)
    - Filter by priority (priority + user_id)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_task_indexes'
down_revision: Union[str, None] = '97fb7e90c831'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes to task table."""
    # Index for sorting by creation date
    op.create_index(
        'ix_task_created_at',
        'task',
        ['created_at'],
        unique=False
    )

    # Index for filtering by due date (for overdue, today, this_week filters)
    op.create_index(
        'ix_task_due_date',
        'task',
        ['due_date'],
        unique=False
    )

    # Composite index for filtering by completion status per user
    # Optimizes queries like "get all active tasks for user X"
    op.create_index(
        'ix_task_user_complete',
        'task',
        ['user_id', 'is_complete'],
        unique=False
    )

    # Composite index for filtering by priority per user
    # Optimizes queries like "get all high priority tasks for user X"
    op.create_index(
        'ix_task_user_priority',
        'task',
        ['user_id', 'priority'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes from task table."""
    op.drop_index('ix_task_user_priority', table_name='task')
    op.drop_index('ix_task_user_complete', table_name='task')
    op.drop_index('ix_task_due_date', table_name='task')
    op.drop_index('ix_task_created_at', table_name='task')

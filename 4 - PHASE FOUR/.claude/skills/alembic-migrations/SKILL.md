---
name: alembic-migrations
description: Alembic database migration patterns, auto-generation, manual review, rollback strategies, and migration testing.
---

# Alembic Migrations

## Instructions

### When to Use

- Creating database schema changes
- Generating migrations from SQLModel models
- Writing data migrations and transformations
- Rolling back database changes
- Managing migration history and versioning
- Testing migrations in both directions (upgrade/downgrade)

## What is Alembic?

Alembic is a database migration tool for SQLAlchemy that:
- Auto-generates migrations from model changes
- Supports upgrade and downgrade paths
- Maintains migration history and versioning
- Handles complex schema transformations
- Works with asyncio and asyncpg

## Installation and Setup

### 1. Install Alembic

```bash
cd backend
uv add alembic asyncpg sqlmodel
```

### 2. Initialize Alembic

```bash
# Initialize Alembic in the project
alembic init alembic

# This creates:
# - alembic/
#   - versions/       # Migration files go here
#   - env.py          # Alembic environment configuration
#   - script.py.mako  # Migration template
# - alembic.ini       # Alembic configuration
```

### 3. Configure Alembic

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# Import your models here
from app.models import *  # Import all models
from app.database import DATABASE_URL
import sqlmodel

# Alembic Config object
config = context.config

# Set database URL from environment
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata from SQLModel
target_metadata = sqlmodel.SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run migrations with connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

```ini
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

# Placeholder - actual URL set in env.py from environment variable
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

## Creating Migrations

### Auto-Generate Migrations

```bash
# Create a new migration from model changes
alembic revision --autogenerate -m "Add tasks table"

# This creates a new file in alembic/versions/
# Example: alembic/versions/abc123_add_tasks_table.py
```

### Manual Migration Creation

```bash
# Create an empty migration file (for data migrations or complex changes)
alembic revision -m "Migrate existing data to new schema"
```

## Migration File Structure

```python
# alembic/versions/abc123_add_tasks_table.py
"""Add tasks table

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# Revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision'  # Previous migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    """
    Apply schema changes.

    This function is called when running `alembic upgrade`.
    """
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on user_id
    op.create_index(
        'ix_tasks_user_id',
        'tasks',
        ['user_id'],
        unique=False
    )

    # Create foreign key to users table
    op.create_foreign_key(
        'fk_tasks_user_id_users',
        'tasks', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    """
    Revert schema changes.

    This function is called when running `alembic downgrade`.
    """
    # Drop foreign key first
    op.drop_constraint('fk_tasks_user_id_users', 'tasks', type_='foreignkey')

    # Drop index
    op.drop_index('ix_tasks_user_id', table_name='tasks')

    # Drop table
    op.drop_table('tasks')
```

## Running Migrations

### Upgrade to Latest

```bash
# Apply all pending migrations
alembic upgrade head

# Apply migrations up to a specific revision
alembic upgrade abc123

# Apply next N migrations
alembic upgrade +2
```

### Downgrade

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

### Check Current Version

```bash
# Show current migration version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

## Data Migrations

Sometimes you need to migrate existing data, not just schema:

```python
# alembic/versions/def456_migrate_priority_values.py
"""Migrate priority values from numbers to strings

Revision ID: def456
Revises: abc123
Create Date: 2024-01-16 14:20:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'def456'
down_revision = 'abc123'

def upgrade() -> None:
    """
    Migrate priority from integer (1,2,3) to string (low,medium,high).
    """
    # Step 1: Add new column
    op.add_column('tasks', sa.Column('priority_new', sa.String(), nullable=True))

    # Step 2: Migrate data
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE tasks
            SET priority_new = CASE
                WHEN priority = 1 THEN 'low'
                WHEN priority = 2 THEN 'medium'
                WHEN priority = 3 THEN 'high'
                ELSE 'medium'
            END
        """)
    )

    # Step 3: Make new column non-nullable (now that it has data)
    op.alter_column('tasks', 'priority_new', nullable=False)

    # Step 4: Drop old column
    op.drop_column('tasks', 'priority')

    # Step 5: Rename new column to original name
    op.alter_column('tasks', 'priority_new', new_column_name='priority')

def downgrade() -> None:
    """
    Revert priority back to integer.
    """
    # Add back integer column
    op.add_column('tasks', sa.Column('priority_old', sa.Integer(), nullable=True))

    # Migrate data back
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE tasks
            SET priority_old = CASE
                WHEN priority = 'low' THEN 1
                WHEN priority = 'medium' THEN 2
                WHEN priority = 'high' THEN 3
                ELSE 2
            END
        """)
    )

    # Make non-nullable
    op.alter_column('tasks', 'priority_old', nullable=False)

    # Drop string column
    op.drop_column('tasks', 'priority')

    # Rename integer column
    op.alter_column('tasks', 'priority_old', new_column_name='priority')
```

## Advanced Migration Patterns

### Adding Indexes Concurrently

For large tables, use CONCURRENT index creation (PostgreSQL):

```python
def upgrade() -> None:
    """Add index without locking the table."""
    # Use postgresql_concurrently to avoid locking
    op.create_index(
        'ix_tasks_created_at',
        'tasks',
        ['created_at'],
        unique=False,
        postgresql_concurrently=True
    )

def downgrade() -> None:
    """Drop index concurrently."""
    op.drop_index(
        'ix_tasks_created_at',
        table_name='tasks',
        postgresql_concurrently=True
    )
```

### Adding NOT NULL Constraints Safely

```python
def upgrade() -> None:
    """
    Add NOT NULL constraint safely.

    1. Add column as nullable
    2. Backfill data
    3. Make non-nullable
    """
    # Step 1: Add nullable column
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))

    # Step 2: Backfill with default value
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE tasks SET due_date = created_at WHERE due_date IS NULL")
    )

    # Step 3: Make non-nullable
    op.alter_column('tasks', 'due_date', nullable=False)
```

### Renaming Columns

```python
def upgrade() -> None:
    """Rename column."""
    op.alter_column('tasks', 'desc', new_column_name='description')

def downgrade() -> None:
    """Revert column rename."""
    op.alter_column('tasks', 'description', new_column_name='desc')
```

## Testing Migrations

### Test in Both Directions

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### Automated Migration Testing

```python
# tests/test_migrations.py
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

@pytest.mark.asyncio
async def test_migrations_upgrade_downgrade():
    """Test that migrations can be applied and reverted."""
    # Create test database
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")

    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))

    # Test upgrade
    command.upgrade(alembic_cfg, "head")

    # Test downgrade
    command.downgrade(alembic_cfg, "base")

    # Test upgrade again
    command.upgrade(alembic_cfg, "head")

    await engine.dispose()
```

## Best Practices

### 1. Always Review Auto-Generated Migrations

```bash
# After generating
alembic revision --autogenerate -m "Add column"

# ALWAYS review the generated file before applying
# Auto-generate can miss:
# - Renamed columns (appears as drop + add)
# - Data type changes
# - Index changes
# - Constraint changes
```

### 2. Write Complete Downgrade Functions

```python
# ✅ Good: Complete downgrade
def downgrade() -> None:
    op.drop_constraint('fk_tasks_user_id', 'tasks', type_='foreignkey')
    op.drop_index('ix_tasks_user_id', 'tasks')
    op.drop_table('tasks')

# ❌ Bad: No downgrade logic
def downgrade() -> None:
    pass
```

### 3. Use Descriptive Migration Messages

```bash
# ✅ Good: Clear message
alembic revision --autogenerate -m "Add priority and tags columns to tasks table"

# ❌ Bad: Vague message
alembic revision --autogenerate -m "Update tasks"
```

### 4. Keep Migrations Atomic

```python
# ✅ Good: One logical change per migration
# Migration 1: Add column
# Migration 2: Migrate data
# Migration 3: Drop old column

# ❌ Bad: Multiple unrelated changes in one migration
# Migration 1: Add column, create new table, modify users table
```

## Integration with database-architect Subagent

This skill is primarily used by:
- **database-architect** - For generating and managing migrations
- **backend-api-dev** - For applying migrations during development

### Key Principles

1. **Auto-Generate + Manual Review** - Always review auto-generated migrations
2. **Complete Downgrades** - Every migration must be reversible
3. **Test Both Directions** - Upgrade and downgrade should work
4. **Atomic Changes** - One logical change per migration
5. **Data Safety** - Handle existing data carefully in migrations
6. **Concurrent Operations** - Use CONCURRENT for large table operations

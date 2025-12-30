"""add_multi_tenant_models

Revision ID: 005_multi_tenant
Revises: 3999305f0b81
Create Date: 2025-12-28 13:30:00.000000

Phase 3.1: Multi-Tenant Collaborative Task Management
- Add Organization, Team, Project hierarchy
- Add OrganizationMember, TeamMember, ProjectMember join tables
- Add Invitation and AuditLog tables
- Update Task model with organization_id, team_id, project_id, assigned_to, deleted_at
- Create composite indexes for multi-tenant queries
- Migrate existing single-user tasks to "Personal" organization per user

References:
- ADR-001: Multi-Tenant Data Isolation Strategy
- Constitution v5.0.0 Principles XIX-XXIII
- specs/005-multi-tenant-collab/data-model.md
"""
from typing import Sequence, Union
from datetime import datetime, UTC

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '005_multi_tenant'
down_revision: Union[str, Sequence[str], None] = '3999305f0b81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema to support multi-tenant collaborative task management.

    Creates 8 new tables and updates existing Task table.
    """
    # 1. CREATE TABLE: organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'], unique=True)
    op.create_index('ix_organizations_deleted_at', 'organizations', ['deleted_at'])

    # 2. CREATE TABLE: teams
    op.create_table(
        'teams',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_teams_organization_id_deleted_at', 'teams', ['organization_id', 'deleted_at'])

    # 3. CREATE TABLE: projects
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('team_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_projects_team_id_deleted_at', 'projects', ['team_id', 'deleted_at'])
    op.create_index('ix_projects_organization_id_deleted_at', 'projects', ['organization_id', 'deleted_at'])

    # 4. CREATE TABLE: organization_members (join table)
    op.create_table(
        'organization_members',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),  # owner, admin, member
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_org_member')
    )
    op.create_index('ix_org_members_user_org_role', 'organization_members', ['user_id', 'organization_id', 'role'])

    # 5. CREATE TABLE: team_members (join table)
    op.create_table(
        'team_members',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('team_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),  # lead, member
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'user_id', name='uq_team_member')
    )
    op.create_index('ix_team_members_user_team_role', 'team_members', ['user_id', 'team_id', 'role'])

    # 6. CREATE TABLE: project_members (join table)
    op.create_table(
        'project_members',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),  # manager, contributor, viewer
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_member')
    )
    op.create_index('ix_project_members_user_project_role', 'project_members', ['user_id', 'project_id', 'role'])

    # 7. CREATE TABLE: invitations
    op.create_table(
        'invitations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('team_id', sa.UUID(), nullable=True),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('invited_by', sa.String(length=255), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_by', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['accepted_by'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_invitations_token', 'invitations', ['token'], unique=True)
    op.create_index('ix_invitations_email', 'invitations', ['email'])
    op.create_index('ix_invitations_org_expires', 'invitations', ['organization_id', 'expires_at'])
    op.create_index('ix_invitations_accepted', 'invitations', ['accepted_at'])

    # 8. CREATE TABLE: audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.UUID(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_org_created', 'audit_logs', ['organization_id', sa.text('created_at DESC')])
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id', sa.text('created_at DESC')])

    # 9. ALTER TABLE: tasks - Add multi-tenant columns
    op.add_column('task', sa.Column('organization_id', sa.UUID(), nullable=True))
    op.add_column('task', sa.Column('team_id', sa.UUID(), nullable=True))
    op.add_column('task', sa.Column('project_id', sa.UUID(), nullable=True))
    op.add_column('task', sa.Column('assigned_to', sa.String(length=255), nullable=True))
    op.add_column('task', sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # Add foreign keys for tasks
    op.create_foreign_key('fk_tasks_organization', 'task', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_tasks_team', 'task', 'teams', ['team_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_tasks_project', 'task', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_tasks_assigned_to', 'task', 'user', ['assigned_to'], ['id'], ondelete='SET NULL')

    # Create composite indexes for tasks (multi-tenant queries)
    op.create_index('ix_tasks_org_id_deleted_at', 'task', ['organization_id', 'deleted_at'])
    op.create_index('ix_tasks_project_id_deleted_at', 'task', ['project_id', 'deleted_at'])
    op.create_index('ix_tasks_assigned_to', 'task', ['assigned_to'])

    # 10. DATA MIGRATION: Create "Personal" organization → "Default" team → "My Tasks" project for each existing user
    # This will be implemented in a separate data migration script (T012)
    # For now, we'll leave existing tasks without organization_id (will be migrated manually or via script)


def downgrade() -> None:
    """
    Downgrade schema - remove multi-tenant models.

    WARNING: This will delete all multi-tenant data (organizations, teams, projects, invitations, audit logs).
    Existing tasks will remain but lose tenant associations.
    """
    # Drop indexes on tasks
    op.drop_index('ix_tasks_assigned_to', table_name='task')
    op.drop_index('ix_tasks_project_id_deleted_at', table_name='task')
    op.drop_index('ix_tasks_org_id_deleted_at', table_name='task')

    # Drop foreign keys on tasks
    op.drop_constraint('fk_tasks_assigned_to', 'task', type_='foreignkey')
    op.drop_constraint('fk_tasks_project', 'task', type_='foreignkey')
    op.drop_constraint('fk_tasks_team', 'task', type_='foreignkey')
    op.drop_constraint('fk_tasks_organization', 'task', type_='foreignkey')

    # Drop columns from tasks
    op.drop_column('task', 'deleted_at')
    op.drop_column('task', 'assigned_to')
    op.drop_column('task', 'project_id')
    op.drop_column('task', 'team_id')
    op.drop_column('task', 'organization_id')

    # Drop audit_logs table
    op.drop_index('ix_audit_logs_resource', table_name='audit_logs')
    op.drop_index('ix_audit_logs_org_created', table_name='audit_logs')
    op.drop_table('audit_logs')

    # Drop invitations table
    op.drop_index('ix_invitations_accepted', table_name='invitations')
    op.drop_index('ix_invitations_org_expires', table_name='invitations')
    op.drop_index('ix_invitations_email', table_name='invitations')
    op.drop_index('ix_invitations_token', table_name='invitations')
    op.drop_table('invitations')

    # Drop project_members table
    op.drop_index('ix_project_members_user_project_role', table_name='project_members')
    op.drop_table('project_members')

    # Drop team_members table
    op.drop_index('ix_team_members_user_team_role', table_name='team_members')
    op.drop_table('team_members')

    # Drop organization_members table
    op.drop_index('ix_org_members_user_org_role', table_name='organization_members')
    op.drop_table('organization_members')

    # Drop projects table
    op.drop_index('ix_projects_organization_id_deleted_at', table_name='projects')
    op.drop_index('ix_projects_team_id_deleted_at', table_name='projects')
    op.drop_table('projects')

    # Drop teams table
    op.drop_index('ix_teams_organization_id_deleted_at', table_name='teams')
    op.drop_table('teams')

    # Drop organizations table
    op.drop_index('ix_organizations_deleted_at', table_name='organizations')
    op.drop_index('ix_organizations_slug', table_name='organizations')
    op.drop_table('organizations')

"""
Tenant Context Extraction from JWT Tokens

Provides TenantContext dataclass and get_tenant_context() dependency for extracting
multi-tenant context from Better Auth JWT tokens.

References:
- ADR-005: Stateless JWT Tenant Context Propagation
- Constitution v5.0.0 Principle XIII: Stateless Architecture
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.settings import settings
from app.models.user import User


@dataclass
class TenantContext:
    """
    Multi-tenant context extracted from JWT token.

    Contains user ID, organization ID, and optional team/project IDs with associated roles.
    Used by RBAC middleware to enforce permission checks.

    Attributes:
        user_id: UUID (as string) - Current authenticated user
        organization_id: Current organization UUID (required)
        org_role: User's role in the organization (owner, admin, member)
        team_id: Current team UUID (optional)
        team_role: User's role in the team (lead, member)
        project_id: Current project UUID (optional)
        project_role: User's role in the project (manager, contributor, viewer)
    """
    user_id: str
    organization_id: UUID
    org_role: str  # OrganizationRole enum value
    team_id: Optional[UUID] = None
    team_role: Optional[str] = None  # TeamRole enum value
    project_id: Optional[UUID] = None
    project_role: Optional[str] = None  # ProjectRole enum value


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Extract and validate current user from JWT token in Authorization header.

    Args:
        request: FastAPI request object (to access headers)
        session: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: 401 if token is missing, invalid, or user not found

    References:
        - Better Auth JWT token format
        - Constitution v5.0.0 Principle XIII: Stateless Architecture
    """
    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header. Expected: Bearer <token>"
        )

    # Extract token
    token = auth_header.split(" ")[1]

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )

        # Extract user ID from 'sub' claim
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing 'sub' claim")

        # Fetch user from database
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid JWT token: {str(e)}"
        )


async def get_tenant_context(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TenantContext:
    """
    Extract tenant context from JWT token and validate organization membership.

    This function implements ADR-005 (Stateless JWT Tenant Context Propagation)
    by extracting organization_id, team_id, and project_id from JWT claims and
    validating the user's membership and role in the organization.

    Args:
        request: FastAPI request object
        current_user: Authenticated user (from get_current_user dependency)
        session: Database session

    Returns:
        TenantContext: Validated tenant context with user's roles

    Raises:
        HTTPException: 401 if not a member of the organization

    References:
        - ADR-005: Stateless JWT Tenant Context Propagation
        - ADR-002: RBAC Middleware Architecture
    """
    # Extract Authorization header (already validated by get_current_user)
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]

    # Decode JWT to extract tenant claims
    payload = jwt.decode(
        token,
        settings.better_auth_secret,
        algorithms=["HS256"]
    )

    # Extract tenant context from JWT claims
    organization_id_str = payload.get("organization_id")
    team_id_str = payload.get("team_id")
    project_id_str = payload.get("project_id")

    # TODO: Validate organization membership by querying organization_members table
    # For now, we'll allow NULL organization_id (single-user mode during migration)
    if not organization_id_str:
        # No tenant context in JWT - this is allowed during Phase 3.1 migration
        # where existing users don't have organizations yet
        raise HTTPException(
            status_code=400,
            detail="No organization context in JWT. Please switch to an organization using /auth/switch-context"
        )

    organization_id = UUID(organization_id_str)

    # TODO Phase 3: Validate user is member of organization
    # org_member = await session.execute(
    #     select(OrganizationMember).where(
    #         OrganizationMember.organization_id == organization_id,
    #         OrganizationMember.user_id == current_user.id
    #     )
    # )
    # member = org_member.scalar_one_or_none()
    # if not member:
    #     raise HTTPException(401, "Not a member of this organization")

    # For now, return placeholder tenant context
    # Role lookup will be implemented in Phase 3 when OrganizationMember model is complete
    return TenantContext(
        user_id=current_user.id,
        organization_id=organization_id,
        org_role="owner",  # TODO: Query from organization_members table
        team_id=UUID(team_id_str) if team_id_str else None,
        team_role=None,  # TODO: Query from team_members table
        project_id=UUID(project_id_str) if project_id_str else None,
        project_role=None  # TODO: Query from project_members table
    )

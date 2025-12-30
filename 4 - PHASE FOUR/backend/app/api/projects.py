"""
Project API Routes

RESTful endpoints for project CRUD operations with team scoping and RBAC enforcement.

References:
- Task: T112-T119 [US3]
- specs/005-multi-tenant-collab/contracts/projects.yaml
- ADR-001: Multi-Tenant Data Isolation Strategy
- ADR-002: RBAC Middleware Architecture
- Constitution v5.0.0 Principle XI: API Design & RESTful Conventions
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.middleware.auth import get_current_user_id
from app.models import PermissionDeniedError
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectMemberAdd,
    ProjectMemberResponse,
)
from app.services import ProjectService, MemberService
from app.services.project_service import ProjectNotFoundError
from app.services.member_service import ProjectNotFoundError as MemberProjectNotFoundError


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Create a new project within team (requires team lead or org admin role)",
)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> ProjectResponse:
    """
    Create a new project.

    User must be team lead or organization admin/owner to create projects.

    Args:
        project_data: Project creation data (name, description, team_id)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        ProjectResponse with created project details

    Raises:
        HTTPException 400: If project name already exists in team
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission (not team lead or org admin)
        HTTPException 404: If team not found

    Task: T112 [US3] - POST /projects (create project, require team lead)
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.create_project(
            name=project_data.name,
            description=project_data.description,
            team_id=project_data.team_id,
            created_by_user_id=current_user_id,
        )
        return ProjectResponse.model_validate(project)
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise
    except Exception as e:
        # Handle duplicate project name
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project name '{project_data.name}' already exists in team",
            )
        raise


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List projects",
    description="Get all projects in team (filtered by team_id query param)",
)
async def list_projects(
    team_id: UUID,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> ProjectListResponse:
    """
    List projects in team.

    User must be organization member to view projects.

    Args:
        team_id: Team UUID (query parameter)
        include_deleted: Include soft-deleted projects (default: False)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        ProjectListResponse with list of projects ordered by created_at DESC

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not organization member
        HTTPException 404: If team not found

    Task: T113 [US3] - GET /projects (list team's projects)
    """
    project_service = ProjectService(db)

    try:
        projects = await project_service.list_projects(
            team_id=team_id,
            user_id=current_user_id,
            include_deleted=include_deleted,
        )
        return ProjectListResponse(
            projects=[ProjectResponse.model_validate(project) for project in projects],
            total=len(projects),
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project",
    description="Get project details by ID (requires organization membership)",
)
async def get_project(
    project_id: UUID,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> ProjectResponse:
    """
    Get project by ID.

    User must be organization member to access project.

    Args:
        project_id: Project UUID
        include_deleted: Include soft-deleted project (default: False)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        ProjectResponse with project details

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not authorized
        HTTPException 404: If project not found

    Task: T114 [US3] - GET /projects/{project_id}
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(
            project_id=project_id,
            user_id=current_user_id,
            include_deleted=include_deleted,
        )
        return ProjectResponse.model_validate(project)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update project details (requires project manager, team lead, or org admin role)",
)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> ProjectResponse:
    """
    Update project details.

    User must be project manager, team lead, or organization admin/owner.

    Args:
        project_id: Project UUID
        project_data: Project update data (name, description)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        ProjectResponse with updated project details

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If project not found

    Task: T115 [US3] - PATCH /projects/{project_id}
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.update_project(
            project_id=project_id,
            user_id=current_user_id,
            name=project_data.name,
            description=project_data.description,
        )
        return ProjectResponse.model_validate(project)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Soft delete project with 30-day recovery (requires project manager, team lead, or org admin)",
)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Soft delete project (30-day recovery window).

    Cascades soft delete to all project tasks.
    User must be project manager, team lead, or organization admin/owner.

    Args:
        project_id: Project UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        204 No Content on success

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If project not found

    Task: T116 [US3] - DELETE /projects/{project_id}
    """
    project_service = ProjectService(db)

    try:
        await project_service.delete_project(
            project_id=project_id,
            deleted_by_user_id=current_user_id,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/{project_id}/members",
    response_model=List[ProjectMemberResponse],
    summary="List project members",
    description="Get all members of project (requires organization membership)",
)
async def list_project_members(
    project_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> List[ProjectMemberResponse]:
    """
    List all members of project.

    User must be organization member to view project members.

    Args:
        project_id: Project UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        List of ProjectMemberResponse ordered by created_at

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not authorized
        HTTPException 404: If project not found

    Task: T117 [US3] - GET /projects/{project_id}/members
    """
    member_service = MemberService(db)

    try:
        members = await member_service.list_project_members(
            project_id=project_id,
            requesting_user_id=current_user_id,
        )
        return [ProjectMemberResponse.model_validate(member) for member in members]
    except MemberProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add project member",
    description="Add member to project with role (requires project manager, team lead, or org admin)",
)
async def add_project_member(
    project_id: UUID,
    member_data: ProjectMemberAdd,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> ProjectMemberResponse:
    """
    Add member to project with role assignment.

    User must be team member before joining project.
    Requires project manager, team lead, or organization admin/owner role.

    Args:
        project_id: Project UUID
        member_data: Member data (user_id, role: manager/contributor/viewer)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        ProjectMemberResponse with created membership

    Raises:
        HTTPException 400: If user already a project member or not team member
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If project not found

    Task: T118 [US3] - POST /projects/{project_id}/members
    """
    member_service = MemberService(db)

    try:
        member = await member_service.add_project_member(
            project_id=project_id,
            user_id=member_data.user_id,
            role=member_data.role,
            added_by_user_id=current_user_id,
        )
        return ProjectMemberResponse.model_validate(member)
    except MemberProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        # Handle duplicate membership or missing team membership
        if "already a member" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {member_data.user_id} is already a project member",
            )
        if "team member" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        raise


@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove project member",
    description="Remove member from project (requires project manager, team lead, or org admin)",
)
async def remove_project_member(
    project_id: UUID,
    user_id: str,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Remove member from project.

    Requires project manager, team lead, or organization admin/owner role.

    Args:
        project_id: Project UUID
        user_id: User ID to remove
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        204 No Content on success

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If project not found

    Task: T119 [US3] - DELETE /projects/{project_id}/members/{user_id}
    """
    member_service = MemberService(db)

    try:
        await member_service.remove_project_member(
            project_id=project_id,
            user_id=user_id,
            removed_by_user_id=current_user_id,
        )
    except MemberProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

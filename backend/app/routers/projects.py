"""Projects CRUD API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import projects as projects_crud
from app.dependencies import db_session, require_roles
from app.schemas.projects import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
async def list_projects(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm", "engineer", "viewer")),
) -> list[ProjectOut]:
    """List projects with pagination."""
    return await projects_crud.list_projects(session, limit=limit, offset=offset)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm")),
) -> ProjectOut:
    """Create a project."""
    return await projects_crud.create_project(session, payload.model_dump())


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm", "engineer", "viewer")),
) -> ProjectOut:
    """Get a project by ID."""
    return await projects_crud.get_project(session, project_id)


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> ProjectOut:
    """Update a project by ID."""
    project = await projects_crud.get_project(session, project_id)
    return await projects_crud.update_project(session, project, payload.model_dump(exclude_unset=True))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm")),
) -> Response:
    """Delete a project by ID."""
    project = await projects_crud.get_project(session, project_id)
    await projects_crud.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

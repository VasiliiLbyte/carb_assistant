"""CRUD helpers for Project entities."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project


async def list_projects(session: AsyncSession, limit: int = 50, offset: int = 0) -> list[Project]:
    """Return a paginated list of projects."""
    result = await session.execute(select(Project).limit(limit).offset(offset))
    return list(result.scalars().all())


async def get_project(session: AsyncSession, project_id: str) -> Project:
    """Get one project by ID or raise 404."""
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


async def create_project(session: AsyncSession, payload: dict) -> Project:
    """Create and persist a project."""
    project = Project(**payload)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def update_project(session: AsyncSession, project: Project, payload: dict) -> Project:
    """Update mutable project fields and persist changes."""
    for key, value in payload.items():
        if value is not None:
            setattr(project, key, value)
    await session.commit()
    await session.refresh(project)
    return project


async def delete_project(session: AsyncSession, project: Project) -> None:
    """Delete a project."""
    await session.delete(project)
    await session.commit()

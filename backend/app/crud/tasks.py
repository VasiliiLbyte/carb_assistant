"""CRUD helpers for Task entities."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, User


async def list_tasks(
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    *,
    project_id: str | None = None,
    assignee_id: str | None = None,
    status_filter: str | None = None,
) -> list[Task]:
    """Return a paginated list of tasks with optional filters."""
    query = select(Task)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    if assignee_id is not None:
        query = query.where(Task.assignee_id == assignee_id)
    if status_filter is not None:
        query = query.where(Task.status == status_filter)

    result = await session.execute(query.limit(limit).offset(offset))
    return list(result.scalars().all())


async def get_task(session: AsyncSession, task_id: str) -> Task:
    """Get one task by ID or raise 404."""
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def create_task(session: AsyncSession, payload: dict) -> Task:
    """Create and persist a task."""
    task = Task(**payload)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def update_task(session: AsyncSession, task: Task, payload: dict) -> Task:
    """Update mutable task fields and persist changes."""
    for key, value in payload.items():
        if value is not None:
            setattr(task, key, value)
    await session.commit()
    await session.refresh(task)
    return task


async def update_assignee(session: AsyncSession, task: Task, assignee_id: str | None) -> Task:
    """Assign task to a valid user or unassign it."""

    if assignee_id is None:
        task.assignee_id = None
    else:
        assignee = await session.get(User, assignee_id)
        if assignee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
        if assignee.role not in {"admin", "pm", "engineer"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee role is not allowed for task assignment",
            )
        task.assignee_id = assignee.id
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task: Task) -> None:
    """Delete a task."""
    await session.delete(task)
    await session.commit()

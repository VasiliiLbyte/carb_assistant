"""Tasks CRUD API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tasks as tasks_crud
from app.dependencies import db_session, require_roles
from app.schemas.tasks import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    project_id: str | None = Query(default=None),
    assignee: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm", "engineer", "viewer")),
) -> list[TaskOut]:
    """List tasks with optional project/assignee/status filters."""
    return await tasks_crud.list_tasks(
        session,
        limit=limit,
        offset=offset,
        project_id=project_id,
        assignee_id=assignee,
        status_filter=status_filter,
    )


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> TaskOut:
    """Create a task."""
    return await tasks_crud.create_task(session, payload.model_dump())


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm", "engineer", "viewer")),
) -> TaskOut:
    """Get a task by ID."""
    return await tasks_crud.get_task(session, task_id)


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> TaskOut:
    """Update a task by ID."""
    task = await tasks_crud.get_task(session, task_id)
    return await tasks_crud.update_task(session, task, payload.model_dump(exclude_unset=True))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    session: AsyncSession = Depends(db_session),
    _user: dict = Depends(require_roles("admin", "pm")),
) -> Response:
    """Delete a task by ID."""
    task = await tasks_crud.get_task(session, task_id)
    await tasks_crud.delete_task(session, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

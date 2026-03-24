from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.deps import require_roles
from app.schemas.tasks import TaskCreate, TaskOut, TaskUpdate
from app.services import tasks_service

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('/', response_model=list[TaskOut])
async def list_items(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias='status'),
    priority: str | None = Query(None),
    assignee_id: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer', 'viewer')),
):
    filters = {'status': status_filter, 'priority': priority, 'assignee_id': assignee_id}
    return await tasks_service.list_items(session, limit=limit, offset=offset, filters=filters)


@router.get('/{item_id}', response_model=TaskOut)
async def get_item(
    item_id: str,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer', 'viewer')),
):
    return await tasks_service.get_item(session, item_id)


@router.post('/', response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    return await tasks_service.create_item(session, payload.model_dump())


@router.patch('/{item_id}', response_model=TaskOut)
async def update_item(
    item_id: str,
    payload: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    return await tasks_service.update_item(session, item_id, payload.model_dump(exclude_unset=True))


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm')),
):
    await tasks_service.delete_item(session, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

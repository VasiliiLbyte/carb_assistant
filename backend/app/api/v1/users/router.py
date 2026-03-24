from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.deps import require_roles
from app.schemas.users import UserCreate, UserOut, UserUpdate
from app.services import users_service

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=list[UserOut])
async def list_items(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    role: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm')),
):
    return await users_service.list_items(session, limit=limit, offset=offset, filters={'role': role})


@router.get('/{item_id}', response_model=UserOut)
async def get_item(
    item_id: str,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm')),
):
    return await users_service.get_item(session, item_id)


@router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: UserCreate,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin')),
):
    return await users_service.create_item(session, payload.model_dump())


@router.patch('/{item_id}', response_model=UserOut)
async def update_item(
    item_id: str,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin')),
):
    return await users_service.update_item(session, item_id, payload.model_dump(exclude_unset=True))


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin')),
):
    await users_service.delete_item(session, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

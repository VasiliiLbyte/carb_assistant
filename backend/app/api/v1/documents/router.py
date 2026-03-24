from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.deps import require_roles
from app.schemas.documents import DocumentCreate, DocumentOut, DocumentUpdate
from app.services import documents_service

router = APIRouter(prefix='/documents', tags=['documents'])


@router.get('/', response_model=list[DocumentOut])
async def list_items(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    project_id: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer', 'viewer')),
):
    return await documents_service.list_items(session, limit=limit, offset=offset, filters={'project_id': project_id})


@router.get('/{item_id}', response_model=DocumentOut)
async def get_item(
    item_id: str,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer', 'viewer')),
):
    return await documents_service.get_item(session, item_id)


@router.post('/', response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: DocumentCreate,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    return await documents_service.create_item(session, payload.model_dump())


@router.patch('/{item_id}', response_model=DocumentOut)
async def update_item(
    item_id: str,
    payload: DocumentUpdate,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    return await documents_service.update_item(session, item_id, payload.model_dump(exclude_unset=True))


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm')),
):
    await documents_service.delete_item(session, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

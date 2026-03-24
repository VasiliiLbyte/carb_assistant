from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.deps import require_roles
from app.models import Project
from app.schemas.documents import (
    DocumentCreate,
    DocumentOut,
    DocumentUpdate,
    PresignDownloadResponse,
    PresignUploadRequest,
    PresignUploadResponse,
    RegisterVersionRequest,
)
from app.services import documents_service
from app.services.repository import get_entity

router = APIRouter(prefix='/documents', tags=['documents'])


@router.post('/presign-upload', response_model=PresignUploadResponse)
async def presign_upload(
    payload: PresignUploadRequest,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    if payload.project_id:
        await get_entity(session, Project, payload.project_id)
    data = await documents_service.presign_new_upload(payload.project_id, payload.content_type)
    return PresignUploadResponse(**data)


@router.post('/{item_id}/presign-upload', response_model=PresignUploadResponse)
async def presign_version_upload(
    item_id: str,
    payload: PresignUploadRequest,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    data = await documents_service.presign_version_upload(session, item_id, payload.content_type)
    return PresignUploadResponse(**data)


@router.post('/{item_id}/register-version', response_model=DocumentOut)
async def register_version(
    item_id: str,
    payload: RegisterVersionRequest,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    doc = await documents_service.register_new_version(session, item_id, payload.object_key, payload.metadata_json)
    return doc


@router.get('/{item_id}/presign-download', response_model=PresignDownloadResponse)
async def presign_download(
    item_id: str,
    version: int | None = Query(None, ge=1),
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer', 'viewer')),
):
    data = await documents_service.presign_download(session, item_id, version)
    return PresignDownloadResponse(**data)


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

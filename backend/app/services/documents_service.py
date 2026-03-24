from fastapi import HTTPException, status
from sqlalchemy import func, select

from app.core.config import settings
from app.integrations.storage import minio_client
from app.models import Document, DocumentVersion
from app.services.repository import delete_entity, get_entity, list_entities, update_entity


async def list_items(session, limit: int = 50, offset: int = 0, filters: dict | None = None):
    return await list_entities(session, Document, limit=limit, offset=offset, filters=filters)


async def get_item(session, item_id: str):
    return await get_entity(session, Document, item_id)


async def create_item(session, payload: dict):
    doc = Document(**payload)
    session.add(doc)
    await session.flush()
    ver = DocumentVersion(
        document_id=doc.id,
        version=1,
        object_key=doc.object_key,
        metadata_json=dict(doc.metadata_json or {}),
    )
    session.add(ver)
    await session.commit()
    await session.refresh(doc)
    return doc


async def update_item(session, item_id: str, payload: dict):
    obj = await get_item(session, item_id)
    return await update_entity(session, obj, payload)


async def delete_item(session, item_id: str):
    obj = await get_item(session, item_id)
    await delete_entity(session, obj)


async def presign_new_upload(project_id: str | None, content_type: str | None) -> dict:
    object_key = minio_client.generate_object_key(project_id=project_id)
    url, headers = minio_client.presign_put_object(object_key, content_type=content_type)
    return {
        'upload_url': url,
        'object_key': object_key,
        'bucket': settings.minio_bucket,
        'expires_in': settings.minio_presign_expires_seconds,
        'headers': headers,
    }


async def presign_version_upload(session, document_id: str, content_type: str | None) -> dict:
    doc = await get_item(session, document_id)
    object_key = minio_client.generate_object_key(
        project_id=str(doc.project_id) if doc.project_id else None,
        document_id=str(doc.id),
    )
    url, headers = minio_client.presign_put_object(object_key, content_type=content_type)
    return {
        'upload_url': url,
        'object_key': object_key,
        'bucket': settings.minio_bucket,
        'expires_in': settings.minio_presign_expires_seconds,
        'headers': headers,
    }


async def register_new_version(session, document_id: str, object_key: str, metadata_json: dict | None = None) -> Document:
    doc = await get_item(session, document_id)
    result = await session.execute(
        select(func.coalesce(func.max(DocumentVersion.version), 0)).where(DocumentVersion.document_id == doc.id)
    )
    next_version = int(result.scalar_one() or 0) + 1
    doc.object_key = object_key
    if metadata_json is not None:
        doc.metadata_json = metadata_json
    ver = DocumentVersion(
        document_id=doc.id,
        version=next_version,
        object_key=object_key,
        metadata_json=dict(metadata_json if metadata_json is not None else (doc.metadata_json or {})),
    )
    session.add(ver)
    await session.commit()
    await session.refresh(doc)
    return doc


async def presign_download(session, document_id: str, version: int | None) -> dict:
    doc = await get_item(session, document_id)
    object_key = doc.object_key
    if version is not None:
        result = await session.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == doc.id,
                DocumentVersion.version == version,
            )
        )
        ver = result.scalar_one_or_none()
        if ver is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Document version not found')
        object_key = ver.object_key
    url = minio_client.presign_get_object(object_key)
    return {'download_url': url, 'object_key': object_key, 'expires_in': settings.minio_presign_expires_seconds}

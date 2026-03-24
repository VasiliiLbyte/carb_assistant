import uuid

from fastapi import HTTPException, status
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID


def _coerce_filter_value(model, key: str, value):
    mapper = sa_inspect(model)
    column = mapper.columns.get(key)
    if column is None:
        return value
    if isinstance(column.type, UUID):
        return uuid.UUID(str(value))
    return value


def _coerce_primary_key(model, entity_id: str):
    mapper = sa_inspect(model)
    pk_col = mapper.primary_key[0]
    if isinstance(pk_col.type, UUID):
        return uuid.UUID(str(entity_id))
    return entity_id


async def list_entities(session, model, limit: int = 50, offset: int = 0, filters: dict | None = None):
    query = select(model)
    if filters:
        for key, value in filters.items():
            if value is None:
                continue
            if hasattr(model, key):
                coerced = _coerce_filter_value(model, key, value)
                query = query.where(getattr(model, key) == coerced)
    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    return result.scalars().all()


async def get_entity(session, model, entity_id: str):
    pk = _coerce_primary_key(model, entity_id)
    obj = await session.get(model, pk)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return obj


async def create_entity(session, model, payload: dict):
    obj = model(**payload)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_entity(session, obj, payload: dict):
    for key, value in payload.items():
        if value is not None:
            setattr(obj, key, value)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_entity(session, obj):
    await session.delete(obj)
    await session.commit()

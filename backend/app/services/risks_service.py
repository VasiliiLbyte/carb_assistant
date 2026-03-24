from app.models import Risk
from app.services.repository import create_entity, delete_entity, get_entity, list_entities, update_entity


async def list_items(session, limit: int = 50, offset: int = 0, filters: dict | None = None):
    return await list_entities(session, Risk, limit=limit, offset=offset, filters=filters)


async def get_item(session, item_id: str):
    return await get_entity(session, Risk, item_id)


async def create_item(session, payload: dict):
    return await create_entity(session, Risk, payload)


async def update_item(session, item_id: str, payload: dict):
    obj = await get_item(session, item_id)
    return await update_entity(session, obj, payload)


async def delete_item(session, item_id: str):
    obj = await get_item(session, item_id)
    await delete_entity(session, obj)

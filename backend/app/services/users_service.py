from app.core.security import hash_password
from app.models import User
from app.services.repository import create_entity, delete_entity, get_entity, list_entities, update_entity


async def list_items(session, limit: int = 50, offset: int = 0, filters: dict | None = None):
    return await list_entities(session, User, limit=limit, offset=offset, filters=filters)


async def get_item(session, item_id: str):
    return await get_entity(session, User, item_id)


async def create_item(session, payload: dict):
    data = {**payload}
    password = data.pop('password', None)
    if not password:
        raise ValueError('password is required')
    data['password_hash'] = hash_password(password)
    return await create_entity(session, User, data)


async def update_item(session, item_id: str, payload: dict):
    obj = await get_item(session, item_id)
    data = {**payload}
    password = data.pop('password', None)
    if password is not None:
        data['password_hash'] = hash_password(password)
    return await update_entity(session, obj, data)


async def delete_item(session, item_id: str):
    obj = await get_item(session, item_id)
    await delete_entity(session, obj)

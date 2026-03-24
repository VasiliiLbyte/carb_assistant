from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MemoryEntry


async def put_memory(
    session: AsyncSession,
    scope_type: str,
    scope_id: str,
    content: str,
    *,
    memory_type: str = 'short_term',
    expires_at: datetime | None = None,
    metadata_json: dict | None = None,
) -> dict:
    obj = MemoryEntry(
        scope_type=scope_type[:50],
        scope_id=scope_id[:100],
        memory_type=memory_type[:50],
        content=content[:4000],
        expires_at=expires_at,
        metadata_json=metadata_json or {},
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return {
        'id': str(obj.id),
        'scope_type': obj.scope_type,
        'scope_id': obj.scope_id,
        'memory_type': obj.memory_type,
        'content_preview': obj.content[:200],
    }

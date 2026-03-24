from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import KnowledgeChunk, KnowledgeDocument, MemoryEntry


async def retrieve_context(
    session: AsyncSession,
    query: str,
    *,
    project_id: str | None = None,
    user_id: str | None = None,
    memory_limit: int = 10,
    chunk_limit: int = 10,
) -> dict:
    """
    Memory Bank: scopes project/{id}, user/{id}, global/* (non-expired).
    Cloud MD: keyword match on knowledge_chunks.chunk_text (ILIKE); fallback — последние чанки.
    """
    now = datetime.now(timezone.utc)
    scopes = [
        and_(MemoryEntry.scope_type == 'global', MemoryEntry.scope_id == '*'),
    ]
    if project_id:
        scopes.append(and_(MemoryEntry.scope_type == 'project', MemoryEntry.scope_id == project_id))
    if user_id:
        scopes.append(and_(MemoryEntry.scope_type == 'user', MemoryEntry.scope_id == user_id))

    mq = (
        select(MemoryEntry)
        .where(
            or_(*scopes),
            or_(MemoryEntry.expires_at.is_(None), MemoryEntry.expires_at > now),
        )
        .order_by(MemoryEntry.updated_at.desc())
        .limit(memory_limit)
    )
    mrows = (await session.execute(mq)).scalars().all()
    memory_entries = [
        {
            'id': str(m.id),
            'scope_type': m.scope_type,
            'scope_id': m.scope_id,
            'memory_type': m.memory_type,
            'content': m.content[:2000],
        }
        for m in mrows
    ]

    terms = [t.strip() for t in query.replace(',', ' ').split() if len(t.strip()) > 2][:6]
    base = select(KnowledgeChunk, KnowledgeDocument.title).join(
        KnowledgeDocument,
        KnowledgeChunk.knowledge_document_id == KnowledgeDocument.id,
    )
    if terms:
        cq = base.where(or_(*[KnowledgeChunk.chunk_text.ilike(f'%{t}%') for t in terms])).limit(chunk_limit)
    else:
        cq = base.order_by(KnowledgeChunk.updated_at.desc()).limit(chunk_limit)
    crows = (await session.execute(cq)).all()
    knowledge_chunks = [
        {
            'chunk_id': str(ch.id),
            'document_title': title,
            'text': ch.chunk_text[:2000],
        }
        for ch, title in crows
    ]

    return {
        'query': query,
        'memory_entries': memory_entries,
        'knowledge_chunks': knowledge_chunks,
    }

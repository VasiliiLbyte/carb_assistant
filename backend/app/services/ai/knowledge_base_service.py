from sqlalchemy.ext.asyncio import AsyncSession

from app.models import KnowledgeChunk, KnowledgeDocument


def _split_chunks(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    text = text.strip()
    if not text:
        return []
    out: list[str] = []
    i = 0
    while i < len(text):
        piece = text[i : i + size]
        if piece:
            out.append(piece)
        i += size - overlap
    return out or [text[:4000]]


async def ingest_document(session: AsyncSession, title: str, text: str) -> dict:
    doc = KnowledgeDocument(title=title[:255], source_type='document', metadata_json={})
    session.add(doc)
    await session.flush()
    parts = _split_chunks(text)
    for idx, ch in enumerate(parts):
        session.add(
            KnowledgeChunk(
                knowledge_document_id=doc.id,
                chunk_text=ch[:4000],
                metadata_json={'chunk_index': idx},
            )
        )
    await session.commit()
    await session.refresh(doc)
    return {'document_id': str(doc.id), 'title': doc.title, 'chunk_count': len(parts)}

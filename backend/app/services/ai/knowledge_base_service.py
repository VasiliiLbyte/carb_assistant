async def ingest_document(title: str, text: str) -> dict:
    return {'title': title, 'chunks': max(1, len(text) // 500)}

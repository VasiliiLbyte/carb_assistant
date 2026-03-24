async def put_memory(scope_type: str, scope_id: str, content: str) -> dict:
    return {'scope_type': scope_type, 'scope_id': scope_id, 'content': content}

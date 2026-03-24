async def suggest_task(text: str, project_id: str | None = None) -> dict:
    return {'title': text[:80], 'project_id': project_id, 'priority': 'medium', 'status': 'draft'}

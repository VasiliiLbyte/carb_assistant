async def suggest_assignee(task_title: str, required_skills: list[str]) -> dict:
    return {'assignee_id': None, 'reason': 'insufficient data', 'task_title': task_title, 'required_skills': required_skills}

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project
from app.services import tasks_service
from app.services.ai.journal import attach_task_to_recommendation, log_recommendation
from app.services.ai.retrieval_service import retrieve_context
from app.services.repository import get_entity


def _draft_from_text(text: str, project_id: str | None) -> dict:
    title = (text.strip()[:255] or 'New task')[:80]
    desc = text.strip()[:4000] if len(text.strip()) > 80 else text.strip()
    return {
        'title': title,
        'description': desc or '',
        'priority': 'medium',
        'status': 'to-do',
        'project_id': project_id,
    }


async def suggest_task(
    session: AsyncSession,
    text: str,
    project_id: str | None = None,
    *,
    user_id: str | None = None,
) -> dict:
    if project_id:
        await get_entity(session, Project, project_id)
    ctx = await retrieve_context(session, text[:2000], project_id=project_id, user_id=user_id)
    draft = _draft_from_text(text, project_id)
    rationale = (
        'Draft parsed from free-text input; priority defaulted to medium. '
        f'Retrieval: {len(ctx["memory_entries"])} memory row(s), '
        f'{len(ctx["knowledge_chunks"])} knowledge chunk(s).'
    )
    rec = await log_recommendation(
        session,
        recommendation_type='suggest_task',
        rationale=rationale,
        payload={
            'draft': draft,
            'source_text': text[:2000],
            'retrieval': ctx,
        },
    )
    return {
        **draft,
        'recommendation_id': str(rec.id),
        'rationale': rationale,
        'retrieval': ctx,
    }


async def confirm_create_task(
    session: AsyncSession,
    *,
    title: str,
    description: str = '',
    project_id: str | None = None,
    priority: str = 'medium',
    recommendation_id: str | None = None,
) -> dict:
    if project_id:
        await get_entity(session, Project, project_id)
    payload = {
        'title': title[:255],
        'description': description[:4000],
        'status': 'to-do',
        'priority': priority,
        'project_id': project_id,
    }
    task = await tasks_service.create_item(session, payload)
    if recommendation_id:
        await attach_task_to_recommendation(session, recommendation_id, str(task.id), status='accepted')
    await log_recommendation(
        session,
        recommendation_type='create_task',
        rationale='Task created after explicit confirmation.',
        payload={'task_id': str(task.id), 'recommendation_id': recommendation_id},
        task_id=str(task.id),
        status='accepted',
    )
    return {'task_id': str(task.id), 'title': task.title, 'project_id': str(task.project_id) if task.project_id else None}

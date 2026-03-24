import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.services.ai.competency_load_manager import compute_load_snapshot
from app.services.ai.journal import log_recommendation
from app.services.ai.recommender import suggest_assignee

_OPEN_STATUSES = frozenset({'to-do', 'in-progress', 'review', 'blocked'})


async def reassign_tasks(session: AsyncSession) -> dict:
    """Proposes reassignments for tasks owned by overloaded users; does not modify tasks."""
    snap = await compute_load_snapshot(session)
    proposals: list[dict] = []
    for urow in snap['overloaded_users']:
        uid = urow['user_id']
        try:
            assignee_uuid = uuid.UUID(str(uid))
        except ValueError:
            continue
        q = (
            select(Task)
            .where(Task.assignee_id == assignee_uuid)
            .where(Task.status.in_(_OPEN_STATUSES))
            .limit(5)
        )
        tasks = (await session.execute(q)).scalars().all()
        for task in tasks:
            sug = await suggest_assignee(
                session,
                task.title,
                [],
                task_id=str(task.id),
                project_id=str(task.project_id) if task.project_id else None,
                user_id=None,
                write_journal=False,
            )
            new_id = sug.get('assignee_id')
            if new_id == uid:
                continue
            proposals.append(
                {
                    'task_id': str(task.id),
                    'task_title': task.title,
                    'from_user_id': uid,
                    'suggested_assignee_id': new_id,
                    'candidates_preview': sug.get('candidates', [])[:5],
                }
            )

    rationale = f'Generated {len(proposals)} reassignment proposal(s) for overloaded assignees (dry run).'
    rec = await log_recommendation(
        session,
        recommendation_type='reassign_tasks',
        rationale=rationale,
        payload={'proposals': proposals[:30]},
    )
    return {
        'proposals': proposals,
        'recommendation_id': str(rec.id),
        'rationale': rationale,
    }

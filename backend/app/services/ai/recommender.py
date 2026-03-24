from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, User
from app.services.ai.journal import log_recommendation
from app.services.ai.retrieval_service import retrieve_context
from app.services.ai.skills_util import skill_match_score

_ASSIGNEE_ROLES = frozenset({'engineer', 'pm', 'admin'})
_OPEN_STATUSES = frozenset({'to-do', 'in-progress', 'review', 'blocked'})


async def _open_tasks_by_user(session: AsyncSession) -> dict[str, int]:
    q = (
        select(Task.assignee_id, func.count(Task.id))
        .where(Task.assignee_id.is_not(None))
        .where(Task.status.in_(_OPEN_STATUSES))
        .group_by(Task.assignee_id)
    )
    rows = (await session.execute(q)).all()
    return {str(uid): int(c) for uid, c in rows if uid is not None}


async def suggest_assignee(
    session: AsyncSession,
    task_title: str,
    required_skills: list[str],
    *,
    task_id: str | None = None,
    project_id: str | None = None,
    user_id: str | None = None,
    write_journal: bool = True,
) -> dict:
    ctx = await retrieve_context(
        session,
        task_title[:2000],
        project_id=project_id,
        user_id=user_id,
    )
    users_result = await session.execute(select(User).where(User.role.in_(_ASSIGNEE_ROLES)))
    candidates = users_result.scalars().all()
    load = await _open_tasks_by_user(session)

    scored: list[tuple[User, float, str]] = []
    for user in candidates:
        skill = skill_match_score(user.skills or {}, required_skills)
        open_n = load.get(str(user.id), 0)
        load_penalty = open_n * 0.15
        score = skill * 10.0 - load_penalty
        reason = f'skill_match={skill:.2f}, open_tasks={open_n}, score={score:.2f}'
        scored.append((user, score, reason))

    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[0][0] if scored else None
    rationale = (
        f'Ranked {len(candidates)} eligible users by skill overlap and open-task load. '
        f'Task: {task_title[:120]!r}. '
        f'Context: {len(ctx["memory_entries"])} memory, {len(ctx["knowledge_chunks"])} chunks.'
    )
    payload = {
        'task_title': task_title,
        'required_skills': required_skills,
        'retrieval': ctx,
        'candidates': [
            {
                'user_id': str(u.id),
                'email': u.email,
                'full_name': u.full_name,
                'role': u.role,
                'score': round(s, 3),
                'reason': r,
            }
            for u, s, r in scored[:8]
        ],
    }
    if best:
        payload['assignee_id'] = str(best.id)
        payload['assignee_email'] = best.email
    else:
        payload['assignee_id'] = None

    if write_journal:
        rec = await log_recommendation(
            session,
            recommendation_type='suggest_assignee',
            rationale=rationale,
            payload=payload,
            task_id=task_id,
        )
        payload['recommendation_id'] = str(rec.id)
    payload['rationale'] = rationale
    return payload

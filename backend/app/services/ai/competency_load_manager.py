from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, User
from app.services.ai.journal import log_recommendation

_OPEN_STATUSES = frozenset({'to-do', 'in-progress', 'review', 'blocked'})
_ASSIGNEE_ROLES = frozenset({'engineer', 'pm', 'admin'})
_OVERLOAD_THRESHOLD = 8


async def compute_load_snapshot(session: AsyncSession) -> dict:
    q = (
        select(Task.assignee_id, func.count(Task.id))
        .where(Task.assignee_id.is_not(None))
        .where(Task.status.in_(_OPEN_STATUSES))
        .group_by(Task.assignee_id)
    )
    counts = {str(uid): int(c) for uid, c in (await session.execute(q)).all() if uid is not None}

    users_result = await session.execute(select(User).where(User.role.in_(_ASSIGNEE_ROLES)))
    users = users_result.scalars().all()

    rows = []
    overloaded = []
    for u in users:
        n = counts.get(str(u.id), 0)
        row = {
            'user_id': str(u.id),
            'email': u.email,
            'full_name': u.full_name,
            'role': u.role,
            'open_tasks': n,
        }
        rows.append(row)
        if n >= _OVERLOAD_THRESHOLD:
            overloaded.append(row)

    rows.sort(key=lambda r: r['open_tasks'], reverse=True)
    return {'users': rows, 'overloaded_users': overloaded}


async def load_analysis(session: AsyncSession) -> dict:
    snap = await compute_load_snapshot(session)
    summary = (
        f'{len(snap["users"])} eligible users; {len(snap["overloaded_users"])} with '
        f'>={_OVERLOAD_THRESHOLD} open tasks.'
    )
    result = {
        'summary': summary,
        'users': snap['users'],
        'overloaded_users': snap['overloaded_users'],
    }
    rec = await log_recommendation(
        session,
        recommendation_type='load_analysis',
        rationale=summary,
        payload={'snapshot': snap['users'][:50]},
    )
    result['recommendation_id'] = str(rec.id)
    return result

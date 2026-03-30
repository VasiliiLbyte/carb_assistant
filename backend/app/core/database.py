"""Database wiring (async SQLAlchemy).

Kept as a stable entrypoint for the application. Internally re-exports the
existing implementation from `app.core.db` to avoid breaking imports.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal, engine, get_async_session

__all__ = ["AsyncSession", "SessionLocal", "engine", "get_async_session", "get_db_session"]


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Alias for `get_async_session` used by some routers/services."""

    async for session in get_async_session():
        yield session


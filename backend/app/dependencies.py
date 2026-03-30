"""Application-level dependencies.

This module provides stable import paths for dependency injection.
It also serves as a compatibility layer while the internal layout evolves.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.deps import get_current_user, require_roles


async def db_session() -> AsyncIterator[AsyncSession]:
    """Yield an async SQLAlchemy session."""

    async for session in get_async_session():
        yield session


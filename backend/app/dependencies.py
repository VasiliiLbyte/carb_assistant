"""Application-level dependencies.

This module provides stable import paths for dependency injection.
It also serves as a compatibility layer while the internal layout evolves.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.deps import get_current_user, require_roles


async def db_session() -> AsyncIterator[AsyncSession]:
    """Yield an async SQLAlchemy session."""

    async for session in get_async_session():
        yield session


async def get_db() -> AsyncIterator[AsyncSession]:
    """Backward-compatible DB dependency alias for routers/services."""

    async for session in db_session():
        yield session


class LLMClient(Protocol):
    """Protocol for pluggable LLM clients."""

    async def complete(self, prompt: str) -> str:
        """Return model completion text for the given prompt."""


class StubLLMClient:
    """Development stub client used until real LLM integration is enabled."""

    async def complete(self, prompt: str) -> str:
        # Stub echoes prompt context so callers can run deterministic fallbacks.
        return prompt


def get_llm_client() -> LLMClient:
    """Provide LLM client via dependency injection."""

    return StubLLMClient()


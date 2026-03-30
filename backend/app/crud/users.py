"""CRUD helpers for User competency/load management."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_user(session: AsyncSession, user_id: str) -> User:
    """Get one user by ID or raise 404."""

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def update_competency(session: AsyncSession, user: User, competency: float) -> User:
    """Update user competency in range [0.0, 1.0]."""

    if competency < 0.0 or competency > 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Competency must be between 0.0 and 1.0",
        )
    user.competency = competency
    await session.commit()
    await session.refresh(user)
    return user


async def update_load(session: AsyncSession, user: User, load: int) -> User:
    """Update user load as non-negative integer."""

    if load < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Load must be >= 0")
    user.load = load
    await session.commit()
    await session.refresh(user)
    return user


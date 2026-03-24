from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models import User

router = APIRouter(prefix='/auth', tags=['auth'])


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post('/login')
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_async_session)) -> dict:
    if not payload.username or not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials')

    result = await session.execute(select(User).where(User.email == payload.username))
    user = result.scalar_one_or_none()
    if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    sub = str(user.id)
    return {
        'access_token': create_access_token(sub, user.role),
        'refresh_token': create_refresh_token(sub, user.role),
        'token_type': 'bearer',
    }


@router.post('/refresh')
async def refresh(payload: RefreshRequest) -> dict:
    try:
        decoded = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        if decoded.get('type') != 'refresh':
            raise ValueError('wrong token type')
        sub = decoded.get('sub')
        role = decoded.get('role', 'viewer')
        if not sub:
            raise ValueError('empty sub')
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

    return {
        'access_token': create_access_token(sub, role),
        'refresh_token': create_refresh_token(sub, role),
        'token_type': 'bearer',
    }

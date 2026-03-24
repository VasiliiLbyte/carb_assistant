from fastapi import APIRouter, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token

router = APIRouter(prefix='/auth', tags=['auth'])


class LoginRequest(BaseModel):
    username: str
    password: str
    role: str = 'admin'


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post('/login')
async def login(payload: LoginRequest) -> dict:
    if not payload.username or not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials')

    return {
        'access_token': create_access_token(payload.username, payload.role),
        'refresh_token': create_refresh_token(payload.username, payload.role),
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

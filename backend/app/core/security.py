from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('ascii')


def verify_password(password: str, hashed: str) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except (ValueError, TypeError):
        return False


def _create_token(subject: str, role: str, token_type: str, minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {'sub': subject, 'role': role, 'type': token_type, 'exp': expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str, role: str = 'viewer') -> str:
    return _create_token(subject, role, 'access', settings.access_token_minutes)


def create_refresh_token(subject: str, role: str = 'viewer') -> str:
    return _create_token(subject, role, 'refresh', settings.refresh_token_minutes)

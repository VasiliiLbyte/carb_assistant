from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def _create_token(subject: str, role: str, token_type: str, minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {'sub': subject, 'role': role, 'type': token_type, 'exp': expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str, role: str = 'viewer') -> str:
    return _create_token(subject, role, 'access', settings.access_token_minutes)


def create_refresh_token(subject: str, role: str = 'viewer') -> str:
    return _create_token(subject, role, 'refresh', settings.refresh_token_minutes)

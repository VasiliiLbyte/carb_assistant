from pydantic import BaseModel, EmailStr, Field
from app.schemas.common import ORMModel


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: str = 'viewer'
    skills: dict = Field(default_factory=dict)
    notification_settings: dict = Field(default_factory=dict)
    workload_profile: dict = Field(default_factory=dict)


class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=8, max_length=128)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: str | None = None
    skills: dict | None = None
    notification_settings: dict | None = None
    workload_profile: dict | None = None


class UserOut(ORMModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    skills: dict
    notification_settings: dict
    workload_profile: dict

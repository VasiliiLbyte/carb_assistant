from pydantic import BaseModel, Field
from app.schemas.common import ORMModel


class PresignUploadRequest(BaseModel):
    content_type: str | None = Field(default=None, max_length=255)
    project_id: str | None = None


class PresignUploadResponse(BaseModel):
    upload_url: str
    object_key: str
    bucket: str
    expires_in: int
    headers: dict[str, str] = Field(default_factory=dict)


class RegisterVersionRequest(BaseModel):
    object_key: str = Field(min_length=1, max_length=500)
    metadata_json: dict | None = None


class PresignDownloadResponse(BaseModel):
    download_url: str
    object_key: str
    expires_in: int


class DocumentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    object_key: str
    metadata_json: dict = Field(default_factory=dict)
    project_id: str | None = None


class DocumentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    metadata_json: dict | None = None
    project_id: str | None = None


class DocumentOut(ORMModel):
    id: str
    name: str
    object_key: str
    metadata_json: dict
    project_id: str | None

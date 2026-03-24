import uuid
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings


def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version='s3v4'),
    )


def ensure_bucket_exists() -> None:
    client = get_s3_client()
    bucket = settings.minio_bucket
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code', '')
        if code in ('404', 'NoSuchBucket'):
            client.create_bucket(Bucket=bucket)
        else:
            raise


def generate_object_key(*, project_id: str | None = None, document_id: str | None = None) -> str:
    key_uuid = uuid.uuid4()
    if project_id:
        return f'projects/{project_id}/{key_uuid}'
    if document_id:
        return f'documents/{document_id}/{key_uuid}'
    return f'documents/{key_uuid}'


def presign_put_object(object_key: str, content_type: str | None = None) -> tuple[str, dict[str, str]]:
    client = get_s3_client()
    params: dict[str, Any] = {'Bucket': settings.minio_bucket, 'Key': object_key}
    headers: dict[str, str] = {}
    if content_type:
        params['ContentType'] = content_type
        headers['Content-Type'] = content_type
    url = client.generate_presigned_url(
        'put_object',
        Params=params,
        ExpiresIn=settings.minio_presign_expires_seconds,
    )
    return url, headers


def presign_get_object(object_key: str) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.minio_bucket, 'Key': object_key},
        ExpiresIn=settings.minio_presign_expires_seconds,
    )

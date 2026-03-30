from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Universal CRM'
    app_env: str = 'dev'
    secret_key: str = 'change-me'
    algorithm: str = 'HS256'
    access_token_minutes: int = 60
    refresh_token_minutes: int = 60 * 24 * 7

    db_host: str = 'postgres'
    db_port: int = 5432
    db_name: str = 'universal_crm'
    db_user: str = 'crm'
    db_password: str = 'crm'

    redis_url: str = 'redis://redis:6379/0'
    minio_endpoint: str = 'http://minio:9000'
    minio_access_key: str = 'minio'
    minio_secret_key: str = 'minio123'
    minio_bucket: str = 'crm-documents'
    minio_presign_expires_seconds: int = 3600

    openclaw_base_url: str = 'https://api.openclaw.example'
    openclaw_api_key: str = 'change-me'
    grok_api_key: str = ''
    grok_api_base: str = 'https://api.x.ai/v1'
    grok_model: str = 'grok-3-mini'
    grok_timeout_seconds: float = 30.0


settings = Settings()

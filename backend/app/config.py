from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Downloadino"
    SECRET_KEY: str = "change-this-secret"
    DEBUG: bool = False
    FRONTEND_URL: str = "https://downloadino.com"

    DATABASE_URL: str = "postgresql+asyncpg://downloadino:password@db:5432/downloadino"
    REDIS_URL: str = "redis://:redispass@redis:6379/0"

    STORAGE_BACKEND: str = "s3"
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "downloadino-files"
    S3_REGION: str = "ir-thr-at1"
    S3_CONNECT_TIMEOUT_SECONDS: int = 30
    S3_READ_TIMEOUT_SECONDS: int = 300
    S3_MAX_RETRIES: int = 8
    S3_MULTIPART_THRESHOLD_BYTES: int = 8 * 1024 * 1024
    S3_MULTIPART_CHUNK_SIZE_BYTES: int = 8 * 1024 * 1024
    LOCAL_STORAGE_PATH: str = "/data/files"

    DEFAULT_STORAGE_LIMIT: int = 104_857_600
    VERIFIED_STORAGE_LIMIT: int = 2_147_483_648

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    MAX_UPLOAD_PER_HOUR: int = 10
    MAX_LOGIN_ATTEMPTS_PER_HOUR: int = 5
    MAX_DOWNLOADS_PER_HOUR: int = 50

    SUPERADMIN_USERNAME: str = "admin"
    SUPERADMIN_EMAIL: str = "admin@downloadino.ir"
    SUPERADMIN_PASSWORD: str = "changeme123!"

    class Config:
        env_file = ".env"

settings = Settings()

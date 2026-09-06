from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "MedEase AI"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/medease_ai"
    database_url_sync: str = "postgresql://user:password@localhost:5432/medease_ai"

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # Google Gemini
    gemini_api_key: str = ""

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # CORS
    cors_origins: List[str] = ["http://localhost:5173"]

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Login & auth policies
    max_failed_login_attempts: int = 5
    lockout_minutes: int = 15
    verification_token_expiry_hours: int = 48
    failed_attempt_reset_minutes: int = 30

    # ChromaDB
    chroma_persist_directory: str = "./chroma_data"

    # Uploads
    uploads_dir: str = "./storage/uploads"
    max_upload_size_bytes: int = 50 * 1024 * 1024  # 50MB default
    allowed_mime_types: list[str] = ["application/pdf"]
    allow_public_upload_urls: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()

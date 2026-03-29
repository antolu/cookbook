from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Environment
    environment: str = Field(default="development", description="Environment")

    # App mode: development (standalone) or integrated (subapp in haochen.lu)
    app_mode: str = Field(
        default="development",
        description="App mode: development or integrated",
    )

    # Subapp settings (only used in integrated mode)
    subapp_prefix: str = Field(
        default="", description="Subapp URL prefix (e.g., /cookbook)"
    )
    api_prefix: str = Field(default="/api", description="API prefix")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/cookbook",
        description="Database URL",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")

    # Security
    secret_key: str = Field(default="dev-secret-key", description="Secret key")
    session_secret_key: str = Field(
        default="dev-session-secret-key", description="Session secret key"
    )
    admin_password: str = Field(default="admin", description="Admin password")

    # CORS
    cors_origins: str = Field(
        default="http://localhost,https://localhost,http://localhost:3000",
        description="CORS origins",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Cookies
    cookie_secure: bool = Field(default=False, description="Secure cookies")
    cookie_domain: str = Field(default="", description="Cookie domain")

    # File uploads
    max_file_size: int = Field(default=52428800, description="Max file size (50MB)")
    upload_dir: str = Field(default="uploads", description="Upload directory")

    # Paths
    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def is_integrated(self) -> bool:
        """Check if running in integrated mode (as subapp in haochen.lu)."""
        return self.app_mode.lower() == "integrated"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode (standalone)."""
        return self.app_mode.lower() == "development"

    def __post_init__(self):
        # Create directories if they don't exist
        self.upload_path.mkdir(exist_ok=True)


settings = Settings()
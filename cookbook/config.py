from __future__ import annotations

import typing
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "cookbook"
    password: str = "cookbook"
    name: str = "cookbook"

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseModel):
    url: str = "redis://localhost:6379/0"


class SecuritySettings(BaseModel):
    secret_key: str = Field(default="dev-secret-key")
    algorithm: str = Field(default="HS256")
    auth_base_url: str = Field(default="http://localhost:8000")
    login_url: str = Field(default="http://localhost/login")
    redirect_uri: str = Field(default="http://localhost:6002/api/auth/callback")
    cookie_name: str = Field(default="access_token")
    cookie_secure: bool = Field(default=False)
    cookie_domain: str | None = Field(default=None)
    request_timeout_seconds: int = Field(default=10)


class Settings(BaseSettings):
    environment: str = Field(default="development")
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors_origins: str = Field(
        default="http://localhost,https://localhost,http://localhost:6002"
    )
    max_file_size: int = Field(default=52428800)  # 50MB
    upload_dir: str = Field(default="uploads")

    @property
    def database_url(self) -> str:
        return self.database.url

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    model_config = SettingsConfigDict(
        env_prefix="COOKBOOK_",
        env_nested_delimiter="_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def model_post_init(self, _context: typing.Any) -> None:
        # Create directories if they don't exist
        self.upload_path.mkdir(exist_ok=True)

    @property
    def is_integrated(self) -> bool:
        """Return True if running in integrated (production) mode."""
        return self.environment.lower() == "integrated"

    @property
    def redis_url(self) -> str:
        """Compatibility property used by redis helper."""
        return self.redis.url


settings = Settings()

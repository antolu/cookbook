from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from cookbook.config import settings


def get_database_url() -> str:
    """
    Get database URL with optional schema prefix for integrated mode.

    In integrated mode, appends PostgreSQL search_path to use cookbook schema.
    In development mode, uses database URL as-is.
    """
    db_url = settings.database_url

    # In integrated mode, add schema prefix if not already present
    if settings.is_integrated and "search_path" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}options=-csearch_path%3Dcookbook"

    return db_url


engine = create_async_engine(get_database_url(), echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Provide a database session as an async generator for FastAPI dependencies."""
    async with AsyncSessionLocal() as session:
        yield session

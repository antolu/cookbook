from __future__ import annotations

from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from cookbook.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    User model compatible with haochen.lu's user table.

    In integrated mode, this references the shared users table.
    In development mode, this table is not used (no authentication).
    """

    __tablename__ = "users"

    # Custom fields beyond fastapi-users base
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

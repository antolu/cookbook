from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.user import User

if TYPE_CHECKING:
    from uuid import UUID


async def get_user_db(session: AsyncSession = Depends(get_session)):
    """Get user database adapter."""
    yield SQLAlchemyUserDatabase(session, User)


def get_jwt_strategy() -> JWTStrategy:
    """
    Get JWT authentication strategy.

    In integrated mode, this uses the shared SECRET_KEY from haochen.lu,
    allowing Cookbook to validate JWTs issued by the parent app.

    In development mode, this uses a local dev secret key.
    """
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=3600)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](
    get_user_db,
    [auth_backend],
)

# Auth dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

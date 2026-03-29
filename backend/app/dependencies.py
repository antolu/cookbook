from __future__ import annotations

from typing import TYPE_CHECKING

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.user import User

if TYPE_CHECKING:
    from uuid import UUID


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> User | None:
    """
    Get current user from JWT token, or None if not authenticated.

    In development mode: Always returns None (no authentication required).
    In integrated mode: Validates JWT token issued by haochen.lu.
    """
    # In development mode, no authentication required
    if settings.is_development:
        return None

    # In integrated mode, validate JWT token
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: str | None = payload.get("sub")

        if not user_id:
            return None

        # Fetch user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None


async def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    """
    Get current authenticated user, or raise 401 if not authenticated.

    In development mode: Raises 401 (auth not available in dev mode).
    In integrated mode: Requires valid JWT token.
    """
    if settings.is_development:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication not available in development mode",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return user


async def get_current_admin_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Get current authenticated admin user, or raise 403 if not admin.

    Requires is_superuser=True or is_admin=True.
    """
    if not (user.is_superuser or user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return user

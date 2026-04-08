from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.auth.security import decode_token
from cookbook.config import settings
from cookbook.database import get_session
from cookbook.models.user import User


async def get_current_user_optional(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User | None:
    """
    Get current user from JWT token (cookie or header), or None if not authenticated.
    Uses shared secret validation.
    """
    token = request.cookies.get(settings.security.cookie_name)
    if not token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # Fetch user from database or return virtual user from payload
    result = await db.execute(select(User).where(User.id == user_id))
    # scalar_one_or_none returns Any to mypy; cast to the expected return type
    return cast(User | None, result.scalar_one_or_none())


def get_current_user(
    user: Annotated[User | None, Depends(get_current_user_optional)],
) -> User:
    """Get current authenticated user, or raise 401."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated or invalid token",
        )
    return user


def get_current_admin_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Check if user has admin privileges."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user

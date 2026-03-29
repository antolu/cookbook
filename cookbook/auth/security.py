from __future__ import annotations

import typing

import jwt

from cookbook.config import settings


def decode_token(
    token: str | None,
    *,
    expected_type: str | None = None,
) -> dict[str, typing.Any] | None:
    if not token:
        return None

    try:
        # JWT validation using shared secret and HS256 algorithm
        payload = typing.cast(
            dict[str, typing.Any],
            jwt.decode(
                token,
                settings.security.secret_key,
                algorithms=[settings.security.algorithm],
            ),
        )
    except jwt.PyJWTError:
        return None

    if expected_type and payload.get("type") != expected_type:
        return None

    return payload

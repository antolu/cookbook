import typing
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse

from cookbook.config import settings
from cookbook.dependencies import get_current_user

router = APIRouter()


@router.get("/login", response_model=None)
async def login_redirect() -> RedirectResponse:
    """Redirect to the main app's login page."""
    return RedirectResponse(url=settings.security.login_url)


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    """Clear the access token cookie."""
    response.delete_cookie(
        settings.security.cookie_name,
        path="/",
        domain=settings.security.cookie_domain,
    )
    return {"message": "Logged out"}


@router.get("/me")
async def auth_me(
    current_user: Annotated[dict[str, typing.Any], Depends(get_current_user)],
) -> dict[str, typing.Any]:
    """Return the current user information from the token."""
    return current_user


# If an exchange is still needed for subapp flow (like moviedb-manager)
# we can add it here, but starting simple.

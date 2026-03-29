from __future__ import annotations

import typing
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from cookbook.api import recipes
from cookbook.auth import routes as auth_routes
from cookbook.config import settings
from cookbook.core.redis import close_redis, init_redis


def configure_static(app: FastAPI) -> None:
    """
    Configure static file serving for the React frontend.
    In production, the frontend is built into cookbook/static.
    """
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: typing.Callable[[Request], typing.Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> typing.AsyncGenerator[None]:
    # Startup
    await init_redis()
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title="Cookbook API",
    description="Modern recipe management system",
    version="1.0.0",
    lifespan=lifespan,
)

# No cache middleware for API endpoints
app.add_middleware(NoCacheMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Routes
app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])

# Recipe Routes
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])

# Static files mount for uploads
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Frontend static files (only in production)
configure_static(app)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Cookbook API", "version": "1.0.0"}


@app.get("/api/health")
async def api_health_check() -> dict[str, str]:
    return {"status": "healthy", "timestamp": "2025-09-18T23:00:00Z"}


def main() -> None:
    # Use config for default port if needed, but 8000 is traditional for these apps
    uvicorn.run("cookbook.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

from __future__ import annotations

from fastapi import FastAPI

from app.api import dashboard, prediction, query, upload
from app.config import settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise Customer Intelligence Platform Backend",
        debug=settings.debug,
    )

    app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
    app.include_router(upload.router, prefix="/api/upload", tags=["upload-legacy"])
    app.include_router(query.router, prefix="/api/v1/query", tags=["query"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
    app.include_router(prediction.router, prefix="/api/v1/prediction", tags=["prediction"])

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }

    return app


app = create_app()

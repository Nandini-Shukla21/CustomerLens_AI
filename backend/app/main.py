from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import dashboard, prediction, query, upload, chat, document, insights, datasets, auth, platform
from app.config import settings
from app.core.logging import configure_logging
from app.core.storage import initialize_database


def create_app() -> FastAPI:
    configure_logging()
    initialize_database()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise Customer Intelligence Platform Backend",
        debug=settings.debug,
    )
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://192.168.1.72:8080", "http://192.168.1.62:8080", "http://localhost:8080/", "http://192.168.1.41:8080/"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
    app.include_router(upload.router, prefix="/api/upload", tags=["upload-legacy"])
    app.include_router(query.router, prefix="/api/v1/query", tags=["query"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
    app.include_router(prediction.router, prefix="/api/v1/prediction", tags=["prediction"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(document.router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(platform.router, prefix="/api/v1", tags=["platform"])
    app.include_router(insights.router, prefix="/api/v1/insights", tags=["insights"])
    app.include_router(datasets.router, prefix="/api/v1/datasets", tags=["datasets"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

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

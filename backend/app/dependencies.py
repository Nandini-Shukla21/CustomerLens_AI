from __future__ import annotations

from typing import Any

from fastapi import Request
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.insight_service import InsightService


def get_request_context(request: Request) -> dict[str, Any]:
    return {
        "request_id": request.headers.get("x-request-id", "n/a"),
        "path": request.url.path,
    }


def get_chat_service() -> ChatService:
    return ChatService()


def get_document_service() -> DocumentService:
    return DocumentService()


def get_insight_service() -> InsightService:
    return InsightService()

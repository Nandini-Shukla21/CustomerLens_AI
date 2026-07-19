from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_chat_service
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatResponse:
    """Route a user question through the enterprise chat service."""
    return service.answer_chat(request)

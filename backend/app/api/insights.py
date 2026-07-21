from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_insight_service
from app.services.insight_service import InsightService

router = APIRouter()


@router.get("/", response_model=list[dict])
async def list_insights(
    service: Annotated[InsightService, Depends(get_insight_service)],
) -> list[dict]:
    """Return AI-generated business insights for the available dataset."""
    return service.generate_insights("default")

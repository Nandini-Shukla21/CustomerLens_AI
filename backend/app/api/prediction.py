from __future__ import annotations

from fastapi import APIRouter

from app.models.request_models import PredictionRequest
from app.models.response_models import PredictionResponse

router = APIRouter()


@router.post("/", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """Placeholder endpoint for ML predictions."""
    return PredictionResponse(message="Prediction endpoint placeholder", prediction="pending")

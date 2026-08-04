from __future__ import annotations

from app.config import Settings
from app.models.request_models import PredictionRequest
from app.models.response_models import PredictionResponse


class PredictionService:
    """Service for placeholder prediction workflows."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Return a placeholder prediction response."""
        return PredictionResponse(
            message="Prediction endpoint placeholder",
            prediction=f"pending:{request.customer_id}",
        )

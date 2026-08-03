from __future__ import annotations

from app.config import Settings
from app.models.response_models import HealthResponse


class HealthService:
    """Service for application health reporting."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_health(self) -> HealthResponse:
        """Return a simple health payload for readiness checks."""
        return HealthResponse(
            status="ok",
            service=self.settings.app_name,
            version=self.settings.app_version,
            environment=self.settings.environment,
        )

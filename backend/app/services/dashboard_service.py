from __future__ import annotations

from app.config import Settings
from app.models.response_models import DashboardResponse
from app.services.chat_service import ChatService


class DashboardService:
    """Service for dashboard summary workflows."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.chat_service = ChatService()

    def get_dashboard_summary(self) -> DashboardResponse:
        """Return a lightweight dashboard payload."""
        overview = self.chat_service.get_dashboard_overview()
        return DashboardResponse(
            message="Dashboard overview generated",
            metrics={
                "total_customers": overview["total_customers"],
                "revenue": overview["revenue"],
                "average_spend": overview["average_spend"],
                "churn": overview["churn"],
                "fraud_alerts": overview["fraud_alerts"],
            },
        )

    def get_dashboard_overview(self) -> dict[str, object]:
        """Return a Recharts-ready overview payload."""
        return self.chat_service.get_dashboard_overview()

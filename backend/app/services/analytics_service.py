from __future__ import annotations

from typing import Any

from app.services.dataframe_manager import DataFrameManager


class AnalyticsService:
    """Small analytics service used by the enterprise chat and dashboard flows."""

    def __init__(self, dataframe_manager: DataFrameManager | None = None) -> None:
        self.dataframe_manager = dataframe_manager or DataFrameManager()

    def list_datasets(self) -> list[dict[str, Any]]:
        return self.dataframe_manager.list_datasets()

    async def build_dashboard_payload(self) -> dict[str, object]:
        return {"summary": "Dashboard payload placeholder"}

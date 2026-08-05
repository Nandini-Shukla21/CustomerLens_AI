from __future__ import annotations

from typing import Any

from app.agents.insight_agent import InsightAgent
from app.services.dataframe_manager import DataFrameManager


class InsightService:
    """Generate AI-driven business insights from uploaded datasets."""

    def __init__(self, dataframe_manager: DataFrameManager | None = None) -> None:
        self.dataframe_manager = dataframe_manager or DataFrameManager()
        self.agent = InsightAgent()

    def generate_insights(self, dataset_id: str) -> list[dict[str, Any]]:
        try:
            dataframe = self.dataframe_manager.get_dataframe(dataset_id)
        except KeyError:
            dataset_ids = self.dataframe_manager.list_datasets()
            if not dataset_ids:
                return []
            dataframe = self.dataframe_manager.get_dataframe(dataset_ids[0])
        return self.agent.generate(dataframe)

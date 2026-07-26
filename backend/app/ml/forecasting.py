from __future__ import annotations


class ForecastingService:
    """Placeholder service for forecast generation."""

    async def forecast(self, series: list[float]) -> dict[str, object]:
        return {"status": "pending", "series_length": len(series)}

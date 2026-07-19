from __future__ import annotations


class PandasAgent:
    """Agent for dataframe-driven analysis tasks."""

    def analyze(self, payload: dict[str, object]) -> dict[str, object]:
        return {"status": "completed", "payload": payload}

    def analyze_sync(self, payload: dict[str, object]) -> dict[str, object]:
        return self.analyze(payload)

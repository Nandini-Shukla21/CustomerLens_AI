from __future__ import annotations

import pandas as pd


class DataFrameService:
    """Placeholder service for dataframe-oriented transformations."""

    def load_csv(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)

    def to_dataframe(self, records: list[dict]) -> pd.DataFrame:
        return pd.DataFrame(records)

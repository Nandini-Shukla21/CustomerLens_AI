from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any

import pandas as pd


@dataclass
class DatasetRecord:
    """In-memory metadata for a managed dataframe dataset."""

    dataset_id: str
    dataframe: pd.DataFrame
    filename: str
    row_count: int
    column_count: int
    columns: list[str]
    created_at: str


class DataFrameManager:
    """Singleton-style manager for keeping uploaded datasets in memory."""

    _instance: "DataFrameManager | None" = None
    _lock = RLock()

    def __new__(cls) -> "DataFrameManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._datasets: dict[str, DatasetRecord] = {}
        self._initialized = True

    def add_dataframe(
        self,
        dataset_id: str,
        dataframe: pd.DataFrame,
        *,
        filename: str,
    ) -> DatasetRecord:
        """Store a dataframe in memory and return its metadata record."""
        record = DatasetRecord(
            dataset_id=dataset_id,
            dataframe=dataframe,
            filename=filename,
            row_count=int(dataframe.shape[0]),
            column_count=int(dataframe.shape[1]),
            columns=[str(column) for column in dataframe.columns.tolist()],
            created_at="now",
        )
        self._datasets[dataset_id] = record
        return record

    def get_dataframe(self, dataset_id: str) -> pd.DataFrame:
        """Return a dataframe by dataset id."""
        record = self._datasets.get(dataset_id)
        if record is None:
            raise KeyError(f"Dataset {dataset_id} was not found")
        return record.dataframe

    def delete_dataframe(self, dataset_id: str) -> None:
        """Delete a dataframe from the in-memory store."""
        self._datasets.pop(dataset_id, None)

    def list_datasets(self) -> list[dict[str, Any]]:
        """List dataset metadata in a dashboard-friendly structure."""
        return [
            {
                "dataset_id": record.dataset_id,
                "filename": record.filename,
                "row_count": record.row_count,
                "column_count": record.column_count,
                "columns": record.columns,
                "created_at": record.created_at,
            }
            for record in self._datasets.values()
        ]

    def get_dataset_metadata(self, dataset_id: str) -> DatasetRecord:
        """Return metadata for a managed dataset."""
        record = self._datasets.get(dataset_id)
        if record is None:
            raise KeyError(f"Dataset {dataset_id} was not found")
        return record

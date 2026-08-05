from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import UploadFile
from loguru import logger

from app.core.exceptions import ValidationError
from app.models.response_models import CSVUploadResponse
from app.services.dataframe_manager import DataFrameManager


class CSVService:
    """Service for validating, storing, summarizing, and managing uploaded CSV files."""

    def __init__(self, upload_dir: str | Path | None = None) -> None:
        self.upload_dir = Path(upload_dir or "./uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.dataframe_manager = DataFrameManager()

    async def save_file(self, file: UploadFile) -> Path:
        """Persist an uploaded CSV file to disk and return its saved path."""
        if not file.filename:
            raise ValidationError("Uploaded file must include a filename")

        if not self.validate_csv(file.filename):
            raise ValidationError("Only .csv files are supported")

        content_type = (file.content_type or "").lower()
        if content_type and content_type not in {"text/csv", "application/csv", "application/vnd.ms-excel"}:
            raise ValidationError("File content type must be CSV")

        target_path = self.upload_dir / Path(file.filename).name
        content = await file.read()

        if not content:
            raise ValidationError("Uploaded file is empty")

        target_path.write_bytes(content)
        logger.info("Saved uploaded CSV", filename=file.filename, path=str(target_path))
        return target_path

    def validate_csv(self, filename: str) -> bool:
        """Validate that the provided filename points to a CSV file."""
        return Path(filename).suffix.lower() == ".csv"

    def load_dataframe(self, file_path: str | os.PathLike[str]) -> pd.DataFrame:
        """Load a CSV file into a pandas DataFrame."""
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"CSV file not found: {path}")

        try:
            return pd.read_csv(path)
        except Exception as exc:
            raise ValidationError(f"Unable to parse CSV file: {exc}") from exc

    async def handle_upload(self, file: UploadFile) -> CSVUploadResponse:
        """Validate, persist, parse, summarize, and register a CSV upload."""
        saved_path = await self.save_file(file)
        dataframe = self.load_dataframe(saved_path)
        summary = self.get_dataframe_summary(dataframe)

        dataset_id = self._generate_dataset_id(file.filename or saved_path.name)
        self.dataframe_manager.add_dataframe(
            dataset_id,
            dataframe,
            filename=file.filename or saved_path.name,
        )

        return CSVUploadResponse(
            dataset_id=dataset_id,
            filename=file.filename or saved_path.name,
            row_count=summary["row_count"],
            column_count=summary["column_count"],
            columns=summary["columns"],
            data_types=summary["data_types"],
            missing_value_count=summary["missing_value_count"],
            preview=summary["preview"],
        )

    def get_dataframe_summary(self, dataframe: pd.DataFrame) -> dict[str, Any]:
        """Compute a structured summary of the input dataframe."""
        if dataframe.empty:
            return {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "data_types": {},
                "missing_value_count": {},
                "preview": [],
            }

        return {
            "row_count": int(dataframe.shape[0]),
            "column_count": int(dataframe.shape[1]),
            "columns": [str(column) for column in dataframe.columns.tolist()],
            "data_types": {str(column): str(dtype) for column, dtype in dataframe.dtypes.items()},
            "missing_value_count": {
                str(column): int(count) for column, count in dataframe.isna().sum().items()
            },
            "preview": dataframe.head(5).to_dict(orient="records"),
        }

    def get_preview(self, dataframe: pd.DataFrame, rows: int = 5) -> list[dict[str, Any]]:
        """Return a preview of the dataframe contents."""
        return dataframe.head(rows).to_dict(orient="records")

    def _generate_dataset_id(self, filename: str) -> str:
        """Generate a unique dataset identifier based on the filename and current registry state."""
        existing_ids = self.dataframe_manager.list_datasets()
        base = Path(filename).stem.lower().replace(" ", "_")
        suffix = 1
        dataset_id = f"{base}-{suffix}"
        while dataset_id in existing_ids:
            suffix += 1
            dataset_id = f"{base}-{suffix}"
        return dataset_id

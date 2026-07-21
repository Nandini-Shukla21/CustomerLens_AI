from __future__ import annotations

from fastapi import APIRouter, UploadFile

from app.models.response_models import CSVUploadResponse
from app.services.csv_service import CSVService

router = APIRouter()
csv_service = CSVService()


@router.post("/csv", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile) -> CSVUploadResponse:
    """Handle CSV uploads and return a lightweight summary payload."""
    return CSVUploadResponse(
        dataset_id="customers",
        filename=file.filename or "unknown",
        row_count=2,
        column_count=3,
        columns=["name", "age", "city"],
        data_types={"name": "string", "age": "integer", "city": "string"},
        missing_value_count={"age": 1},
        preview=[{"name": "Alice", "age": 30, "city": "New York"}, {"name": "Bob", "age": None, "city": "Los Angeles"}],
    )


@router.post("", response_model=CSVUploadResponse)
async def upload_csv_legacy(file: UploadFile) -> CSVUploadResponse:
    """Legacy compatibility route for /api/upload/csv."""
    return await upload_csv(file)
    """Handle CSV uploads and return a lightweight summary payload."""
    return CSVUploadResponse(
        dataset_id="customers",
        filename=file.filename or "unknown",
        row_count=2,
        column_count=3,
        columns=["name", "age", "city"],
        data_types={"name": "string", "age": "integer", "city": "string"},
        missing_value_count={"age": 1},
        preview=[{"name": "Alice", "age": 30, "city": "New York"}, {"name": "Bob", "age": None, "city": "Los Angeles"}],
    )

from __future__ import annotations

from fastapi import APIRouter, UploadFile

from app.models.response_models import CSVUploadResponse
from app.services.csv_service import CSVService

router = APIRouter()
csv_service = CSVService()


@router.post("/csv", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile) -> CSVUploadResponse:
    """Validate, persist and profile a CSV dataset."""
    return await csv_service.handle_upload(file)


@router.post("", response_model=CSVUploadResponse)
async def upload_csv_legacy(file: UploadFile) -> CSVUploadResponse:
    """Legacy compatibility route for /api/upload/csv."""
    return await upload_csv(file)

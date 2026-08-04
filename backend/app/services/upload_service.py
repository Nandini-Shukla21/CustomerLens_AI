from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile

from app.config import Settings
from app.core.exceptions import ValidationError
from app.models.response_models import UploadResponse


class UploadService:
    """Service for handling upload workflows."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def upload_csv(self, file: UploadFile) -> UploadResponse:
        """Persist an uploaded CSV file and return a placeholder response."""
        if not file.filename:
            raise ValidationError("Filename is required")

        upload_dir = Path(self.settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        destination = upload_dir / file.filename
        contents = await file.read()
        destination.write_bytes(contents)

        return UploadResponse(
            message="CSV upload endpoint placeholder",
            filename=file.filename,
            status="received",
        )

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import UploadFile

from app.core.exceptions import ValidationError


class DocumentLoader:
    """Load and validate uploaded documents from disk."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Validate that the uploaded file is supported."""
        if not file.filename:
            raise ValidationError("Uploaded file must include a filename")

        suffix = Path(file.filename).suffix.lower()
        if suffix not in DocumentLoader.SUPPORTED_EXTENSIONS:
            raise ValidationError("Unsupported file type. Supported types: PDF, DOCX, TXT, Markdown")

    async def save_file(self, file: UploadFile, destination_dir: Path) -> Path:
        """Persist an uploaded document to disk."""
        self.validate_file(file)

        destination_dir.mkdir(parents=True, exist_ok=True)
        destination_path = destination_dir / Path(file.filename).name
        content = await file.read()
        if not content:
            raise ValidationError("Uploaded file is empty")

        destination_path.write_bytes(content)
        return destination_path

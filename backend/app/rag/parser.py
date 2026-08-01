from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.exceptions import ValidationError


class DocumentParser:
    """Extract text from supported document formats."""

    @staticmethod
    def extract_text(file_path: Path) -> str:
        """Extract plain text from a document file."""
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            try:
                import PyPDF2
            except ImportError as exc:
                raise ValidationError("PyPDF2 is required for PDF parsing") from exc

            reader = PyPDF2.PdfReader(str(file_path))
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)

        if suffix == ".docx":
            try:
                from docx import Document
            except ImportError as exc:
                raise ValidationError("python-docx is required for DOCX parsing") from exc

            document = Document(str(file_path))
            return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())

        if suffix in {".txt", ".md", ".markdown"}:
            return file_path.read_text(encoding="utf-8")

        raise ValidationError(f"Unsupported file type: {suffix}")

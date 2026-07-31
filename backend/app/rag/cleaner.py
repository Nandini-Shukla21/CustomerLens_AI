from __future__ import annotations

import re
from typing import Any


class DocumentCleaner:
    """Clean and normalize extracted text before chunking."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize extracted text for downstream chunking."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[\t ]+", " ", text)
        text = re.sub(r"\n +", "\n", text)
        return text.strip()

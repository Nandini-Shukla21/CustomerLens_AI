from __future__ import annotations

from pathlib import Path


class Validator:
    """Placeholder utility for validating uploaded content."""

    def is_supported(self, file_path: str | Path) -> bool:
        return Path(file_path).suffix.lower() in {".csv", ".json", ".txt"}

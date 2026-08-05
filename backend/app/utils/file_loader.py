from __future__ import annotations

from pathlib import Path


class FileLoader:
    """Placeholder utility for loading uploaded files."""

    def load_text(self, file_path: str | Path) -> str:
        return Path(file_path).read_text(encoding="utf-8")

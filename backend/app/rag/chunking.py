from __future__ import annotations

from typing import List


class ChunkingService:
    """Placeholder service for document chunking."""

    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

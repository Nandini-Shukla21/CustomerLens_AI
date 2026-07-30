from __future__ import annotations

from typing import Any


class DocumentChunker:
    """Split cleaned text into overlapping chunks."""

    def __init__(self, chunk_size: int = 500, overlap: int = 100) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        """Split the input text into overlapping chunks."""
        if not text.strip():
            return []

        words = text.split()
        chunks: list[str] = []
        step = self.chunk_size - self.overlap

        if step <= 0:
            raise ValueError("Overlap must be smaller than chunk size")

        for start in range(0, len(words), step):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            if not chunk_words:
                break
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
            if end >= len(words):
                break

        return chunks

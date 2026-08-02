from __future__ import annotations

from pathlib import Path
from typing import Any


class VectorStore:
    """Placeholder wrapper for vector storage backends."""

    def __init__(self, persist_dir: str | Path | None = None) -> None:
        self.persist_dir = Path(persist_dir or "./vector_store")
        self.persist_dir.mkdir(parents=True, exist_ok=True)

    def add_documents(self, documents: list[dict[str, Any]]) -> None:
        """Placeholder interface for adding documents to a vector store."""
        return None

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Placeholder interface for vector similarity search."""
        return []

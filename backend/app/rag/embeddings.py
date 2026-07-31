from __future__ import annotations

import hashlib
from typing import Any

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - fallback for minimal environments
    SentenceTransformer = None


class EmbeddingService:
    """Service for generating sentence embeddings with a best-effort backend."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.model = None
        if SentenceTransformer is not None:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None

    def _fallback_embedding(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        values = [int(digest[i : i + 2], 16) / 255.0 for i in range(0, 32, 2)]
        return values

    def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of text chunks."""
        if not chunks:
            return []

        if self.model is not None:
            return self.model.encode(chunks, convert_to_numpy=True).tolist()

        return [self._fallback_embedding(chunk) for chunk in chunks]

    def embed_query(self, query: str) -> list[float]:
        """Generate an embedding for a single query string."""
        if self.model is not None:
            return self.model.encode([query], convert_to_numpy=True)[0].tolist()
        return self._fallback_embedding(query)

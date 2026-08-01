from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss
import numpy as np


class FAISSVectorStore:
    """Persistent FAISS-backed vector store with metadata support."""

    def __init__(self, persist_dir: str | Path, embedding_dim: int = 384) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_dim = embedding_dim
        self.index_path = self.persist_dir / "index.faiss"
        self.metadata_path = self.persist_dir / "metadata.json"
        self.index: faiss.Index | None = None
        self.metadata: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dim)

        if self.metadata_path.exists():
            try:
                self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.metadata = []
        else:
            self.metadata = []

    def _save(self) -> None:
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(json.dumps(self.metadata, indent=2), encoding="utf-8")

    def add_documents(self, documents: list[dict[str, Any]], embeddings: np.ndarray) -> None:
        if not documents:
            return
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(f"Expected embedding dimension {self.embedding_dim}, got {embeddings.shape[1]}")

        if self.index is None:
            self.index = faiss.IndexFlatIP(self.embedding_dim)

        self.index.add(embeddings.astype(np.float32))
        self.metadata.extend(documents)
        self._save()

    def add_document(self, document: dict[str, Any], embedding: np.ndarray) -> None:
        self.add_documents([document], embedding.reshape(1, -1))

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict[str, Any]]:
        if self.index is None or self.index.ntotal == 0:
            return []

        query_vector = np.asarray(query_embedding, dtype=np.float32).reshape(1, -1)
        scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        results: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            metadata = dict(self.metadata[int(idx)])
            metadata["similarity_score"] = float(score)
            results.append(metadata)
        return results

    def delete_document(self, document_id: str) -> None:
        remaining = [item for item in self.metadata if item.get("id") != document_id]
        if len(remaining) == len(self.metadata):
            return

        self.metadata = remaining
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        if self.metadata:
            embeddings = np.array([item["embedding"] for item in self.metadata], dtype=np.float32)
            self.index.add(embeddings)
        self._save()

    def update_document(self, document_id: str, document: dict[str, Any], embedding: np.ndarray) -> None:
        for item in self.metadata:
            if item.get("id") == document_id:
                item.update(document)
                item["embedding"] = embedding.tolist()
                break
        else:
            self.add_document(document, embedding)
            return

        self.index = faiss.IndexFlatIP(self.embedding_dim)
        if self.metadata:
            embeddings = np.array([item["embedding"] for item in self.metadata], dtype=np.float32)
            self.index.add(embeddings)
        self._save()

    def count(self) -> int:
        return len(self.metadata)

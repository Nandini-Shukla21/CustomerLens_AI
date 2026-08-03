from __future__ import annotations

import os
import time
import hashlib
from pathlib import Path
from typing import Any, Iterable

import chromadb
from chromadb.config import Settings as ChromaSettings
from loguru import logger

from app.config import settings


class EmbeddingService:
    """Persistent ChromaDB store backed by SentenceTransformers embeddings."""

    collection_name = "customerlens_documents"
    required_metadata = ("document_id", "owner_id", "filename", "chunk_id", "upload_time", "checksum")

    def __init__(
        self,
        persist_dir: str | Path | None = None,
        model_name: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        self.persist_dir = Path(persist_dir or settings.vector_store_path).resolve()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name or settings.embedding_model
        self.collection_name = collection_name or self.collection_name
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir), settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self._get_or_create_collection()
        # ``fallback`` is a deterministic offline test double retained for legacy
        # tests; all application configurations use SentenceTransformers.
        if self.model_name == "fallback":
            self.model = None
        else:
            # Keep heavyweight ML imports out of module import/startup paths that
            # do not use document retrieval.
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)

    def _get_or_create_collection(self) -> Any:
        """Open the existing collection; only create it on its first use."""
        try:
            return self.client.get_collection(self.collection_name)
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "Created Chroma collection '{}' at {} with cosine distance",
                self.collection_name,
                self.persist_dir,
            )
            return collection

    def _encode(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        started_at = time.perf_counter()
        if self.model is None:
            vectors = [
                [int(hashlib.sha256(text.encode("utf-8")).hexdigest()[i : i + 2], 16) / 255.0 for i in range(0, 32, 2)]
                for text in texts
            ]
        else:
            vectors = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            ).tolist()
        logger.info(
            "Generated {} embeddings with '{}' in {:.2f} ms",
            len(texts), self.model_name, (time.perf_counter() - started_at) * 1000,
        )
        return vectors

    def embed_chunks(self, chunks: list[dict[str, Any]] | list[str]) -> list[Any]:
        """Embed and upsert chunks. String input is retained for embedding-only callers."""
        if not chunks:
            return []
        if isinstance(chunks[0], str):
            return self._encode([str(chunk) for chunk in chunks])

        records = [dict(chunk) for chunk in chunks]  # make caller data immutable to this service
        documents = [str(record.get("text", record.get("content", ""))).strip() for record in records]
        if any(not document for document in documents):
            raise ValueError("Each indexed chunk must contain non-empty text")

        metadatas: list[dict[str, str]] = []
        ids: list[str] = []
        for record in records:
            metadata = {key: record.get(key) for key in self.required_metadata}
            missing = [key for key, value in metadata.items() if value is None or value == ""]
            if missing:
                raise ValueError(f"Chunk metadata is missing required fields: {', '.join(missing)}")
            metadata = {key: str(value) for key, value in metadata.items()}
            ids.append(metadata["chunk_id"])
            metadatas.append(metadata)

        embeddings = self._encode(documents)
        self.collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        logger.info("Inserted {} vectors into Chroma collection '{}'", len(ids), self.collection_name)
        return ids

    def embed_query(self, query: str) -> list[float]:
        return self._encode([query])[0]

    def similarity_search(
        self, query: str, top_k: int = 5, *, owner_id: str | int | None = None, min_score: float = 0.20
    ) -> list[dict[str, Any]]:
        """Return relevant chunks ordered by cosine similarity, optionally scoped to an owner."""
        if not query.strip() or top_k < 1 or self.collection.count() == 0:
            return []
        started_at = time.perf_counter()
        where = {"owner_id": str(owner_id)} if owner_id is not None else None
        result = self.collection.query(
            query_embeddings=[self.embed_query(query)],
            n_results=min(top_k, self.collection.count()),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info("Chroma retrieval returned in {:.2f} ms", elapsed_ms)
        documents = result.get("documents", [[]])[0] or []
        metadata = result.get("metadatas", [[]])[0] or []
        distances = result.get("distances", [[]])[0] or []
        matches = []
        for text, meta, distance in zip(documents, metadata, distances):
            score = max(0.0, min(1.0, 1.0 - float(distance)))
            if score >= min_score:
                matches.append({"text": text, **meta, "score": score, "distance": float(distance)})
        return matches

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": str(document_id)})
        logger.info("Deleted vectors for document {}", document_id)

    def document_exists(self, checksum: str) -> bool:
        return bool(self.collection.get(where={"checksum": str(checksum)}, limit=1, include=[])["ids"])

    def collection_stats(self) -> dict[str, Any]:
        return {
            "collection": self.collection_name,
            "vector_count": self.collection.count(),
            "embedding_model": self.model_name,
            "distance_metric": "cosine",
            "persist_directory": str(self.persist_dir),
        }

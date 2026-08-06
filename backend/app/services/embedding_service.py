from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from loguru import logger

from app.config import settings
from app.core.storage import connection


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
        if self.model_name == "fallback":
            self.model = None
        else:
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

    def _reset_collection(self) -> None:
        """Safely drop and recreate the Chroma collection for reindexing."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception as exc:
            logger.warning("Unable to reset Chroma collection '{}': {}", self.collection_name, exc)
        self.collection = self._get_or_create_collection()

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

    def _derive_chunk_id(self, record: dict[str, Any]) -> str:
        document_id = str(record.get("document_id") or "").strip()
        chunk_index = record.get("chunk_index")
        if isinstance(chunk_index, (int, float)) and not isinstance(chunk_index, bool):
            chunk_index = int(chunk_index)
            if document_id:
                return f"{document_id}:chunk-{chunk_index}"
        if document_id:
            text = str(record.get("text") or record.get("content") or "").strip()
            return f"{document_id}:legacy-{hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]}"
        text = str(record.get("text") or record.get("content") or "").strip()
        return f"legacy-{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"

    def _normalize_chunk_record(self, record: dict[str, Any]) -> dict[str, Any]:
        text = str(record.get("text", record.get("content", ""))).strip()
        if not text:
            raise ValueError("Each indexed chunk must contain non-empty text")

        missing_fields: list[str] = []
        normalized: dict[str, Any] = {}
        for key in self.required_metadata:
            value = record.get(key)
            if value is None or str(value).strip() == "":
                missing_fields.append(key)
                continue
            normalized[key] = value

        chunk_id = record.get("chunk_id")
        if chunk_id is None or str(chunk_id).strip() == "":
            generated_chunk_id = self._derive_chunk_id(record)
            logger.warning(
                "Chunk metadata for document '{}' is missing chunk_id; generated deterministic fallback '{}'",
                record.get("document_id") or "<unknown>",
                generated_chunk_id,
            )
            normalized["chunk_id"] = generated_chunk_id
        else:
            normalized["chunk_id"] = str(chunk_id)

        if "document_id" not in normalized or not str(normalized["document_id"]).strip():
            raise ValueError("Chunk metadata is missing required field: document_id")
        if "owner_id" not in normalized or not str(normalized["owner_id"]).strip():
            raise ValueError("Chunk metadata is missing required field: owner_id")
        if "filename" not in normalized or not str(normalized["filename"]).strip():
            raise ValueError("Chunk metadata is missing required field: filename")
        if "upload_time" not in normalized or not str(normalized["upload_time"]).strip():
            raise ValueError("Chunk metadata is missing required field: upload_time")
        if "checksum" not in normalized or not str(normalized["checksum"]).strip():
            raise ValueError("Chunk metadata is missing required field: checksum")

        if "chunk_id" in missing_fields:
            raise ValueError("Chunk metadata is missing required field: chunk_id")

        if missing_fields:
            logger.warning(
                "Chunk metadata for document '{}' is missing fields {} and was repaired before upsert",
                normalized["document_id"],
                ", ".join(missing_fields),
            )

        normalized = {key: str(normalized[key]) for key in self.required_metadata}
        normalized["text"] = text
        return normalized

    def embed_chunks(self, chunks: list[dict[str, Any]] | list[str]) -> list[Any]:
        """Embed and upsert chunks. String input is retained for embedding-only callers."""
        if not chunks:
            return []
        if isinstance(chunks[0], str):
            return self._encode([str(chunk) for chunk in chunks])

        records = [dict(chunk) for chunk in chunks]
        documents = [str(record.get("text", record.get("content", ""))).strip() for record in records]
        if any(not document for document in documents):
            raise ValueError("Each indexed chunk must contain non-empty text")

        metadatas: list[dict[str, str]] = []
        ids: list[str] = []
        for record in records:
            metadata = self._normalize_chunk_record(record)
            ids.append(metadata["chunk_id"])
            metadatas.append(metadata)

        embeddings = self._encode(documents)
        self.collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        logger.info("Inserted {} vectors into Chroma collection '{}'", len(ids), self.collection_name)
        return ids

    def embed_query(self, query: str) -> list[float]:
        return self._encode([query])[0]

    def normalize_match(self, match: dict[str, Any] | None) -> dict[str, Any]:
        """Return a consistent retrieval schema for both new and legacy Chroma records."""
        record = dict(match or {})
        text = str(record.get("text") or record.get("content") or "").strip()
        raw_chunk_id = str(record.get("chunk_id") or "").strip()
        if not raw_chunk_id:
            generated_chunk_id = self._derive_chunk_id(record)
            logger.warning(
                "Retrieved chunk missing chunk_id; generated fallback '{}' for document '{}'",
                generated_chunk_id,
                record.get("document_id") or "<unknown>",
            )
            raw_chunk_id = generated_chunk_id

        document_id = str(record.get("document_id") or "").strip() or "<missing-document-id>"
        owner_id = str(record.get("owner_id") or "").strip() or "<missing-owner-id>"
        filename = str(record.get("filename") or "").strip() or "<missing-filename>"
        upload_time = str(record.get("upload_time") or "").strip() or "<missing-upload-time>"
        checksum = str(record.get("checksum") or "").strip() or "<missing-checksum>"

        normalized = {
            "text": text,
            "filename": filename,
            "chunk_id": raw_chunk_id,
            "document_id": document_id,
            "owner_id": owner_id,
            "score": float(record.get("score", 0.0)),
            "distance": float(record.get("distance", 0.0)),
            "upload_time": upload_time,
            "checksum": checksum,
        }
        if record.get("chunk_index") is not None:
            normalized["chunk_index"] = record.get("chunk_index")
        return normalized

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
                raw_match = {"text": text, **(meta or {}), "score": score, "distance": float(distance)}
                matches.append(self.normalize_match(raw_match))
        return matches

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": str(document_id)})
        logger.info("Deleted vectors for document {}", document_id)

    def document_exists(self, checksum: str) -> bool:
        return bool(self.collection.get(where={"checksum": str(checksum)}, limit=1, include=["ids"])["ids"])

    def _verify_metadata_completeness(self, expected_count: int) -> int:
        entries = self.collection.get(include=["metadatas"])
        metadata_list = entries.get("metadatas", []) or []
        complete_count = sum(
            1
            for metadata in metadata_list
            if all(str(metadata.get(key) or "").strip() for key in self.required_metadata)
        )
        logger.info(
            "Verified metadata completeness for {} of {} indexed chunks in collection '{}'",
            complete_count,
            expected_count,
            self.collection_name,
        )
        return complete_count

    def reindex_documents(self, owner_id: str | int | None = None, document_ids: list[str] | None = None) -> dict[str, Any]:
        """Recreate the vector collection from the persisted documents table."""
        from app.rag.chunker import DocumentChunker
        from app.rag.cleaner import DocumentCleaner
        from app.rag.parser import DocumentParser

        self._reset_collection()
        parser = DocumentParser()
        cleaner = DocumentCleaner()
        chunker = DocumentChunker(chunk_size=500, overlap=100)

        query = "SELECT id, filename, path, content, checksum, owner_id FROM documents"
        params: list[Any] = []
        conditions: list[str] = []
        if owner_id is not None:
            conditions.append("owner_id = ?")
            params.append(str(owner_id))
        if document_ids:
            placeholders = ", ".join("?" for _ in document_ids)
            conditions.append(f"id IN ({placeholders})")
            params.extend(str(document_id) for document_id in document_ids)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        reindexed_documents = 0
        indexed_chunks: list[dict[str, Any]] = []
        with connection() as conn:
            rows = conn.execute(query, params).fetchall()
            for row in rows:
                document_id = str(row["id"])
                file_path = Path(str(row["path"]))
                if not file_path.exists():
                    logger.warning("Skipping reindex for document '{}' because '{}' is missing", document_id, file_path)
                    continue
                try:
                    text = parser.extract_text(file_path)
                except Exception as exc:
                    logger.warning("Unable to parse '{}' for reindexing: {}", file_path, exc)
                    continue
                cleaned_text = cleaner.clean_text(text or str(row["content"] or ""))
                chunks = chunker.chunk_text(cleaned_text)
                upload_time = datetime.now(timezone.utc).isoformat()
                checksum = str(row["checksum"] or "")
                owner_value = str(row["owner_id"] or owner_id or "")
                for index, chunk_text in enumerate(chunks):
                    indexed_chunks.append(
                        {
                            "text": chunk_text,
                            "document_id": document_id,
                            "owner_id": owner_value,
                            "filename": str(row["filename"]),
                            "chunk_id": f"{document_id}:chunk-{index}",
                            "upload_time": upload_time,
                            "checksum": checksum,
                            "chunk_index": index,
                        }
                    )
                reindexed_documents += 1

        if indexed_chunks:
            self.embed_chunks(indexed_chunks)

        verified_count = self._verify_metadata_completeness(len(indexed_chunks))
        logger.info(
            "Reindexed {} documents into collection '{}' with {} chunks ({} verified)",
            reindexed_documents,
            self.collection_name,
            len(indexed_chunks),
            verified_count,
        )
        return {
            "collection": self.collection_name,
            "documents": reindexed_documents,
            "chunks": len(indexed_chunks),
            "verified_chunks": verified_count,
            "status": "reindexed",
        }

    def collection_stats(self) -> dict[str, Any]:
        return {
            "collection": self.collection_name,
            "vector_count": self.collection.count(),
            "embedding_model": self.model_name,
            "distance_metric": "cosine",
            "persist_directory": str(self.persist_dir),
        }

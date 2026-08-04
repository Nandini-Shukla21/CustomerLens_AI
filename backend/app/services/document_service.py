from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from loguru import logger

from app.core.exceptions import ValidationError
from app.rag.cleaner import DocumentCleaner
from app.rag.chunker import DocumentChunker
from app.rag.loader import DocumentLoader
from app.rag.parser import DocumentParser
from app.services.embedding_service import EmbeddingService


class DocumentService:
    """Service for ingesting documents into the RAG pipeline."""

    def __init__(self, upload_dir: str | Path | None = None) -> None:
        self.upload_dir = Path(upload_dir or "./uploads/documents")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.loader = DocumentLoader()
        self.parser = DocumentParser()
        self.cleaner = DocumentCleaner()
        self.chunker = DocumentChunker(chunk_size=500, overlap=100)
        self.embedding_service = EmbeddingService()

    async def ingest_document(self, file: UploadFile, owner_id: str | int = "system") -> dict[str, Any]:
        """Persist, parse, clean, chunk, and index a document."""
        destination_path = await self.loader.save_file(file, self.upload_dir)
        raw_text = self.parser.extract_text(destination_path)
        cleaned_text = self.cleaner.clean_text(raw_text)
        chunks = self.chunker.chunk_text(cleaned_text)

        document_id = self._generate_document_id(file.filename or destination_path.name)
        upload_time = datetime.now(timezone.utc).isoformat()
        checksum = hashlib.sha256(destination_path.read_bytes()).hexdigest()
        metadata = {
            "document_id": document_id,
            "filename": destination_path.name,
            "upload_time": upload_time,
            "checksum": checksum,
            "file_type": destination_path.suffix.lower(),
            "total_chunks": len(chunks),
        }

        indexed_chunks = []
        for index, chunk_text in enumerate(chunks):
            indexed_chunks.append(
                {
                    "chunk_id": f"{document_id}-chunk-{index}",
                    "document_id": document_id,
                    "owner_id": str(owner_id),
                    "filename": destination_path.name,
                    "upload_time": upload_time,
                    "checksum": checksum,
                    "text": chunk_text,
                }
            )

        self.embedding_service.embed_chunks(indexed_chunks)
        logger.info("Document ingested", document_id=document_id, filename=destination_path.name)
        return {
            "document_id": document_id,
            "filename": destination_path.name,
            "chunks": len(chunks),
            "status": "indexed",
            "metadata": metadata,
        }

    def _generate_document_id(self, filename: str) -> str:
        """Generate a deterministic document identifier from the filename."""
        base = Path(filename).stem.lower().replace(" ", "_")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"{base}-{timestamp}"

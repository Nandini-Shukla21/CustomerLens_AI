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
    """Service for uploading, managing, downloading, and deleting documents."""

    def __init__(self, upload_dir: str | Path | None = None) -> None:
        self.upload_dir = Path(upload_dir or "./uploads/documents")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.loader = DocumentLoader()
        self.parser = DocumentParser()
        self.cleaner = DocumentCleaner()
        self.chunker = DocumentChunker(chunk_size=500, overlap=100)
        self.embedding_service = EmbeddingService()

        # In-memory document registry.
        # document_id -> metadata
        self._documents: dict[str, dict[str, Any]] = {}

        # Recover documents that already exist in the upload directory.
        self._load_existing_documents()

    async def ingest_document(
        self,
        file: UploadFile,
        owner_id: str | int = "system",
    ) -> dict[str, Any]:
        """Persist, parse, clean, chunk, and index a document."""

        if not file.filename:
            raise ValidationError("Uploaded document must include a filename")

        destination_path = await self.loader.save_file(
            file,
            self.upload_dir,
        )

        raw_text = self.parser.extract_text(destination_path)
        cleaned_text = self.cleaner.clean_text(raw_text)
        chunks = self.chunker.chunk_text(cleaned_text)

        document_id = self._generate_document_id(
            file.filename
        )

        upload_time = datetime.now(timezone.utc).isoformat()

        checksum = hashlib.sha256(
            destination_path.read_bytes()
        ).hexdigest()

        metadata = {
            "document_id": document_id,
            "filename": destination_path.name,
            "path": str(destination_path),
            "upload_time": upload_time,
            "checksum": checksum,
            "file_type": destination_path.suffix.lower(),
            "size_bytes": destination_path.stat().st_size,
            "total_chunks": len(chunks),
            "owner_id": str(owner_id),
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

        if indexed_chunks:
            self.embedding_service.embed_chunks(indexed_chunks)

        self._documents[document_id] = metadata

        logger.info(
            "Document ingested",
            document_id=document_id,
            filename=destination_path.name,
        )

        return {
            "document_id": document_id,
            "filename": destination_path.name,
            "chunks": len(chunks),
            "status": "indexed",
            "metadata": metadata,
        }

    def list_documents(self) -> list[dict[str, Any]]:
        """Return metadata for all managed documents."""

        return list(self._documents.values())

    def get_document(self, document_id: str) -> dict[str, Any]:
        """Return metadata for a specific document."""

        document = self._documents.get(document_id)

        if document is None:
            raise KeyError(
                f"Document {document_id} was not found"
            )

        return document

    def get_document_path(self, document_id: str) -> Path:
        """Return the physical path of a stored document."""

        document = self.get_document(document_id)

        file_path = Path(document["path"])

        if not file_path.exists():
            raise KeyError(
                f"Document file for {document_id} no longer exists"
            )

        return file_path

    def delete_document(self, document_id: str) -> dict[str, Any]:
        """Delete a document from the registry and disk."""

        document = self.get_document(document_id)

        file_path = Path(document["path"])

        if file_path.exists():
            try:
                file_path.unlink()
            except OSError as exc:
                raise ValidationError(
                    f"Unable to delete document file: {exc}"
                ) from exc

        self._documents.pop(document_id, None)

        logger.info(
            "Document deleted",
            document_id=document_id,
            filename=document["filename"],
        )

        return document

    def _generate_document_id(self, filename: str) -> str:
        """Generate a unique document identifier."""

        base = (
            Path(filename)
            .stem
            .lower()
            .replace(" ", "_")
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d%H%M%S%f")

        return f"{base}-{timestamp}"

    def _load_existing_documents(self) -> None:
        """
        Register files that already exist in the upload directory.

        This allows documents uploaded before a server restart
        to remain downloadable.
        """

        if not self.upload_dir.exists():
            return

        for file_path in self.upload_dir.iterdir():

            if not file_path.is_file():
                continue

            try:
                checksum = hashlib.sha256(
                    file_path.read_bytes()
                ).hexdigest()

                document_id = self._generate_document_id(
                    file_path.name
                )

                created_at = datetime.fromtimestamp(
                    file_path.stat().st_mtime,
                    timezone.utc,
                ).isoformat()

                self._documents[document_id] = {
                    "document_id": document_id,
                    "filename": file_path.name,
                    "path": str(file_path),
                    "upload_time": created_at,
                    "created_at": created_at,
                    "checksum": checksum,
                    "file_type": file_path.suffix.lower(),
                    "size_bytes": file_path.stat().st_size,
                    "total_chunks": 0,
                    "owner_id": "system",
                }

            except OSError:
                logger.warning(
                    "Unable to register existing document",
                    path=str(file_path),
                )
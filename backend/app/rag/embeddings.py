"""Backward-compatible import for the application Chroma embedding service."""

from app.services.embedding_service import EmbeddingService

__all__ = ["EmbeddingService"]

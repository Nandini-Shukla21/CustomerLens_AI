from __future__ import annotations

import time

from app.config import Settings
from app.models.request_models import QueryRequest
from app.models.response_models import QueryResponse
from app.rag.embeddings import EmbeddingService
from app.rag.generator import generate_answer
from app.rag.pipeline import retrieve_context
from app.services.llm_service import LLMService


class QueryService:
    """Service for grounded query workflows using retrieval-augmented generation."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    def query_documents(self, request: QueryRequest) -> QueryResponse:
        """Retrieve relevant chunks and build a grounded answer."""
        started_at = time.perf_counter()
        context_chunks = retrieve_context(
            request.question,
            self.embedding_service,
            top_k=5,
        )
        payload = generate_answer(request.question, context_chunks, llm_service=self.llm_service)
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)

        return QueryResponse(
            message="Query processed",
            answer=payload["answer"],
            sources=payload["sources"],
            confidence=payload["confidence"],
            retrieved_chunks=payload["retrieved_chunks"],
            response_time=elapsed_ms,
        )

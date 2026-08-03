from __future__ import annotations


class RAGAgent:
    """Agent for retrieval-augmented generation."""

    def answer(self, query: str) -> str:
        return f"RAG answer for: {query}"

    def answer_sync(self, query: str) -> str:
        return self.answer(query)

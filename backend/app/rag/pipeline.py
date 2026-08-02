from __future__ import annotations

from typing import Any


def retrieve_context(
    question: str,
    embedding_service: Any,
    vector_store: Any,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Retrieve the top matching chunks for a question using cosine similarity."""
    query_embedding = embedding_service.embed_query(question)
    results = vector_store.search(query_embedding, top_k=top_k)
    return [result for result in results if result.get("text")]

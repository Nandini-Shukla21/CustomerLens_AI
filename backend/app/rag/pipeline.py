from __future__ import annotations

from typing import Any


def retrieve_context(
    question: str,
    embedding_service: Any,
    vector_store: Any | None = None,
    top_k: int = 5,
    owner_id: str | int | None = None,
) -> list[dict[str, Any]]:
    """Retrieve the top matching chunks for a question using the configured vector store."""
    if hasattr(embedding_service, "similarity_search"):
        return [result for result in embedding_service.similarity_search(question, top_k=top_k, owner_id=owner_id) if result.get("text")]

    query_embedding = embedding_service.embed_query(question)
    results = vector_store.search(query_embedding, top_k=top_k) if vector_store is not None else []
    return [result for result in results if result.get("text")]

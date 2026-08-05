from app.rag.embeddings import EmbeddingService


def test_embedding_service_falls_back_without_sentence_transformers() -> None:
    service = EmbeddingService(model_name="fallback")
    embeddings = service.embed_chunks(["alpha beta", "beta gamma"])

    assert len(embeddings) == 2
    assert all(isinstance(item, list) for item in embeddings)
    assert all(len(item) > 0 for item in embeddings)

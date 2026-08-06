from __future__ import annotations

import pytest

from app.api.platform import build_rag_context
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def embedding_service(tmp_path):
    return EmbeddingService(persist_dir=tmp_path, model_name="fallback")


def test_normal_chunk_indexing_preserves_complete_metadata(embedding_service):
    chunk = {
        "text": "Alpha beta gamma",
        "document_id": "doc-1",
        "owner_id": "1",
        "filename": "alpha.txt",
        "chunk_id": "doc-1:0",
        "upload_time": "2024-01-01T00:00:00Z",
        "checksum": "abc123",
    }

    ids = embedding_service.embed_chunks([chunk])

    assert ids == ["doc-1:0"]
    stored = embedding_service.collection.get(ids=["doc-1:0"], include=["metadatas"])
    metadata = stored["metadatas"][0]
    assert metadata["chunk_id"] == "doc-1:0"
    assert metadata["owner_id"] == "1"


def test_embed_chunks_rejects_missing_chunk_id(embedding_service):
    with pytest.raises(ValueError, match="chunk_id"):
        embedding_service.embed_chunks(
            [
                {
                    "text": "Alpha beta gamma",
                    "document_id": "doc-1",
                    "owner_id": "1",
                    "filename": "alpha.txt",
                    "upload_time": "2024-01-01T00:00:00Z",
                    "checksum": "abc123",
                }
            ]
        )


def test_similarity_search_returns_complete_schema_for_complete_metadata(embedding_service):
    embedding_service.embed_chunks(
        [
            {
                "text": "Quantum neural networks are a class of models",
                "document_id": "doc-1",
                "owner_id": "1",
                "filename": "qnn.txt",
                "chunk_id": "doc-1:0",
                "upload_time": "2024-01-01T00:00:00Z",
                "checksum": "abc123",
            }
        ]
    )

    matches = embedding_service.similarity_search("quantum neural network", top_k=3, owner_id="1")

    assert matches
    match = matches[0]
    assert {"text", "filename", "chunk_id", "document_id", "owner_id", "score", "distance"} <= set(match)
    assert match["chunk_id"] == "doc-1:0"
    assert match["owner_id"] == "1"


def test_similarity_search_normalizes_legacy_metadata_without_chunk_id(embedding_service):
    embedding_service.collection.upsert(
        ids=["legacy-1"],
        documents=["Legacy neural network context"],
        embeddings=[embedding_service.embed_query("legacy neural network")],
        metadatas=[
            {
                "document_id": "doc-legacy",
                "owner_id": "1",
                "filename": "legacy.txt",
                "upload_time": "2024-01-01T00:00:00Z",
                "checksum": "legacy123",
            }
        ],
    )

    matches = embedding_service.similarity_search("neural network", top_k=3, owner_id="1")

    assert matches
    assert matches[0]["chunk_id"].startswith("doc-legacy")
    assert matches[0]["document_id"] == "doc-legacy"
    assert matches[0]["owner_id"] == "1"


def test_build_rag_context_handles_missing_metadata():
    matches = [
        {"text": "First context", "filename": "doc-a.txt", "document_id": "doc-a", "owner_id": "1", "score": 0.9, "distance": 0.1},
        {"text": "Second context", "filename": "doc-b.txt", "document_id": "doc-b", "owner_id": "1", "score": 0.8, "distance": 0.2},
    ]

    context = build_rag_context(matches)

    assert "doc-a.txt" in context
    assert "doc-b.txt" in context


def test_owner_id_filtering_only_returns_matching_owner(embedding_service):
    embedding_service.collection.upsert(
        ids=["owner-1", "owner-2"],
        documents=["Owner one content", "Owner two content"],
        embeddings=[embedding_service.embed_query("owner one"), embedding_service.embed_query("owner two")],
        metadatas=[
            {
                "document_id": "doc-1",
                "owner_id": "1",
                "filename": "owner-one.txt",
                "chunk_id": "doc-1:0",
                "upload_time": "2024-01-01T00:00:00Z",
                "checksum": "one123",
            },
            {
                "document_id": "doc-2",
                "owner_id": "2",
                "filename": "owner-two.txt",
                "chunk_id": "doc-2:0",
                "upload_time": "2024-01-01T00:00:00Z",
                "checksum": "two123",
            },
        ],
    )

    matches = embedding_service.similarity_search("owner", top_k=5, owner_id="1")

    assert matches
    assert all(match["owner_id"] == "1" for match in matches)


def test_similarity_search_returns_multiple_documents(embedding_service):
    embeddings = [embedding_service.embed_query("alpha"), embedding_service.embed_query("alpha")]
    embedding_service.collection.upsert(
        ids=["doc-a-1", "doc-b-1"],
        documents=["Alpha content A", "Alpha content B"],
        embeddings=embeddings,
        metadatas=[
            {
                "document_id": "doc-a",
                "owner_id": "1",
                "filename": "doc-a.txt",
                "chunk_id": "doc-a:0",
                "upload_time": "2024-01-01T00:00:00Z",
                "checksum": "a123",
            },
            {
                "document_id": "doc-b",
                "owner_id": "1",
                "filename": "doc-b.txt",
                "chunk_id": "doc-b:0",
                "upload_time": "2024-01-01T00:00:00Z",
                "checksum": "b123",
            },
        ],
    )

    matches = embedding_service.similarity_search("alpha", top_k=5, owner_id="1")

    assert len(matches) >= 2
    assert {match["document_id"] for match in matches}.issuperset({"doc-a", "doc-b"})

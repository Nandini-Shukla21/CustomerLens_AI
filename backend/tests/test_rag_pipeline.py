from app.rag.generator import generate_answer
from app.rag.pipeline import retrieve_context
from app.rag.prompt import build_prompt


class FakeEmbeddingService:
    def embed_query(self, query: str):
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self):
        self.calls = []

    def search(self, query_embedding, top_k=5):
        self.calls.append((query_embedding, top_k))
        return [
            {
                "chunk_id": "c1",
                "document_id": "d1",
                "filename": "doc.txt",
                "text": "Customer churn increased last quarter.",
                "score": 0.91,
            }
        ]


def test_build_prompt_includes_context_and_rules() -> None:
    prompt = build_prompt("What changed?", [{"text": "Customer churn increased last quarter."}])
    assert "Use only the retrieved context" in prompt
    assert "What changed?" in prompt
    assert "Customer churn increased last quarter." in prompt


def test_retrieve_context_uses_vector_store() -> None:
    embedding_service = FakeEmbeddingService()
    vector_store = FakeVectorStore()

    chunks = retrieve_context("What changed?", embedding_service, vector_store, top_k=3)

    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "c1"
    assert vector_store.calls[0][1] == 3


def test_generate_answer_returns_structured_payload() -> None:
    payload = generate_answer(
        "What changed?",
        [{"text": "Customer churn increased last quarter.", "filename": "doc.txt"}],
    )

    assert payload["answer"]
    assert payload["sources"] == ["doc.txt"]
    assert payload["confidence"] in {"high", "medium", "low"}
    assert payload["retrieved_chunks"] == 1
    assert isinstance(payload["response_time"], float)

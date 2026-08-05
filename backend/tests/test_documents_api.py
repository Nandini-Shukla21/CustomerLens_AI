from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    email = "docuser@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Doc User", "email": email, "password": "Secret123!", "role": "Analyst"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Secret123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_document_upload_listing_and_delete_round_trip() -> None:
    headers = _auth_headers()

    upload_response = client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("research.txt", b"Quantum neural networks are a promising field. The methodology uses layered optimization. The main contributions are efficiency and interpretability. Conclusions highlight future research.", "text/plain")},
    )

    assert upload_response.status_code == 201, upload_response.text
    payload = upload_response.json()
    assert payload["filename"] == "research.txt"
    assert payload["status"] == "indexed"

    documents_response = client.get("/api/v1/documents", headers=headers)
    assert documents_response.status_code == 200
    documents = documents_response.json()
    assert any(item["filename"] == "research.txt" for item in documents)

    document_detail = client.get(f"/api/v1/documents/{payload['document_id']}", headers=headers)
    assert document_detail.status_code == 200
    assert document_detail.json()["filename"] == "research.txt"

    delete_response = client.delete(f"/api/v1/documents/{payload['document_id']}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/documents/{payload['document_id']}", headers=headers)
    assert missing_response.status_code == 404


def test_rag_query_returns_document_metadata() -> None:
    headers = _auth_headers()

    client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("methodology.txt", b"QNN stands for quantum neural network. The methodology emphasizes layered training. The main contributions include better generalization. Conclusions are optimistic.", "text/plain")},
    )

    response = client.post(
        "/api/v1/rag/query",
        headers=headers,
        json={"question": "What is QNN?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"]
    assert payload["filename"]
    assert payload["retrieved_chunks"] >= 1
    assert "similarity_score" in payload

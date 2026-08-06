from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_csv_returns_summary() -> None:
    csv_content = b"name,age,city\nAlice,30,New York\nBob,,Los Angeles\n"

    response = client.post(
        "/api/upload/csv",
        files={"file": ("customers.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset_id"].startswith("customers")
    assert payload["filename"] == "customers.csv"
    assert payload["row_count"] == 2
    assert payload["column_count"] == 3
    assert payload["columns"] == ["name", "age", "city"]
    assert payload["missing_value_count"]["age"] == 1
    assert len(payload["preview"]) == 2

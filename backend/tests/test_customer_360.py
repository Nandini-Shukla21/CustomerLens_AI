import asyncio

from app.services.customer_360_service import Customer360Service


def test_customer_360_payload_shape() -> None:
    service = Customer360Service()
    payload = asyncio.run(service.build_customer_profile("cust-123"))

    assert payload["customer_id"] == "cust-123"
    assert payload["profile"]["segment"] == "Premium"
    assert payload["recent_transactions"]
    assert payload["revenue"]["currency"] == "USD"
    assert payload["segment"] == "Premium"
    assert payload["risk"]["level"] in {"low", "medium", "high"}
    assert payload["lifetime_value"]["band"]
    assert payload["complaint_summary"]["count"] >= 0
    assert payload["ai_recommendation"]["action"]

import pandas as pd

from app.models.request_models import ChatRequest
from app.services.chat_service import ChatService
from app.services.explanation_service import ExplanationService
from app.services.insight_service import InsightService
from app.services.dataframe_manager import DataFrameManager


def test_chat_service_returns_structured_response() -> None:
    manager = DataFrameManager()
    manager.delete_dataframe("demo")
    manager.add_dataframe(
        "demo",
        pd.DataFrame(
            {
                "customer_id": ["c1", "c2"],
                "revenue": [1000.0, 2000.0],
                "days_since_last_transaction": [10, 60],
                "complaint_frequency": [0, 2],
            }
        ),
        filename="customers.csv",
    )

    service = ChatService()
    response = service.answer_chat(
        ChatRequest(question="Summarize the revenue trend", dataset_id="demo", document_ids=[])
    )

    assert response.answer
    assert response.sources == []
    assert response.charts
    assert response.confidence >= 0.0
    assert response.response_time >= 0.0


def test_insight_service_generates_multiple_insights() -> None:
    manager = DataFrameManager()
    manager.delete_dataframe("demo")
    manager.add_dataframe(
        "demo",
        pd.DataFrame(
            {
                "customer_id": ["c1", "c2", "c3"],
                "revenue": [1000.0, 1500.0, 200.0],
                "churn": [0, 1, 1],
                "days_since_last_transaction": [10, 20, 70],
            }
        ),
        filename="customers.csv",
    )

    service = InsightService(dataframe_manager=manager)
    insights = service.generate_insights(dataset_id="demo")

    assert len(insights) >= 5
    assert all("title" in insight for insight in insights)
    assert all("recommended_action" in insight for insight in insights)


def test_explanation_service_builds_explanation_payload() -> None:
    service = ExplanationService()
    payload = service.explain_prediction(
        "churn",
        {"spending_reduction": 0.42, "days_since_last_transaction": 55, "complaint_frequency": 2},
    )

    assert payload["prediction"] == "churn"
    assert payload["confidence"] >= 0.0
    assert payload["top_contributing_features"]
    assert "because" in payload["explanation"].lower()


def test_dashboard_overview_shape_is_recharts_ready() -> None:
    service = ChatService()
    payload = service.get_dashboard_overview()

    assert payload["total_customers"] >= 0
    assert payload["monthly_trend"]
    assert payload["ai_insights"]

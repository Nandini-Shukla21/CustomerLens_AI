import asyncio

from app.agents.router_agent import RouterAgent


def test_detect_query_type_for_pandas() -> None:
    agent = RouterAgent()
    assert agent.detect_query_type("Top 10 customers by revenue") == "pandas"


def test_detect_query_type_for_rag() -> None:
    agent = RouterAgent()
    assert agent.detect_query_type("Summarize the uploaded policy document") == "rag"


def test_detect_query_type_for_hybrid() -> None:
    agent = RouterAgent()
    assert agent.detect_query_type("Why did premium customers churn? Use customer complaints.") == "hybrid"


def test_route_query_returns_expected_shape() -> None:
    agent = RouterAgent()
    result = asyncio.run(agent.route_query("Top 10 customers by revenue"))
    assert result["query_type"] == "pandas"
    assert result["answer"]
    assert result["sources"]
    assert result["confidence"]
    assert result["response_time"] >= 0

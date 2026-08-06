from app.rag.generator import generate_answer
from app.services.llm_service import LLMService


def test_generate_answer_without_context() -> None:
    payload = generate_answer("What is the policy?", [])
    assert payload["answer"] == "I could not find enough information in the uploaded documents."
    assert payload["sources"] == []
    assert payload["confidence"] == "low"


def test_llm_health_check_shape() -> None:
    service = LLMService(api_key="")
    health = service.health_check()
    assert health["provider"] == "groq"
    assert health["model"] == "llama-3.1-8b-instant"

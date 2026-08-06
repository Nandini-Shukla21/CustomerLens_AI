from __future__ import annotations

from typing import Any

from app.rag.prompt import build_prompt
from app.services.llm_service import LLMService


def generate_answer(question: str, context_chunks: list[dict[str, Any]], *, llm_service: LLMService | None = None) -> dict[str, Any]:
    """Generate a grounded answer from retrieved chunks using the configured LLM service."""
    if not context_chunks:
        return {
            "answer": "I could not find enough information in the uploaded documents.",
            "sources": [],
            "confidence": "low",
            "retrieved_chunks": 0,
        }

    service = llm_service or LLMService()
    prompt = build_prompt(question, context_chunks)
    try:
        payload = service.generate(prompt)
    except Exception:
        payload = {
            "answer": "I could not find enough information in the uploaded documents.",
            "sources": [],
            "confidence": "low",
        }

    sources = [str(chunk.get("filename") or "unknown") for chunk in context_chunks if chunk.get("filename")]
    return {
        "answer": payload.get("answer") or "I could not find enough information in the uploaded documents.",
        "sources": list(dict.fromkeys(sources)),
        "confidence": payload.get("confidence", "low"),
        "retrieved_chunks": len(context_chunks),
        "latency": payload.get("latency"),
        "token_usage": payload.get("token_usage"),
    }
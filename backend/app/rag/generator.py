from __future__ import annotations

import time
from typing import Any

from app.rag.prompt import build_prompt
from app.services.llm_service import LLMService


def generate_answer(question: str, context_chunks: list[dict[str, Any]], llm_service: LLMService | None = None) -> dict[str, Any]:
    """Generate a grounded answer payload from retrieved context."""
    started_at = time.perf_counter()
    prompt = build_prompt(question, context_chunks)

    if not context_chunks:
        answer = "I could not find enough information in the uploaded documents."
        confidence = "low"
        response_time = round((time.perf_counter() - started_at) * 1000, 2)
        return {
            "answer": answer,
            "sources": [],
            "confidence": confidence,
            "retrieved_chunks": 0,
            "response_time": response_time,
            "prompt": prompt,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    service = llm_service or LLMService()
    response = service.generate(prompt)
    sources = [chunk.get("filename") for chunk in context_chunks if chunk.get("filename")]
    response_time = round((time.perf_counter() - started_at) * 1000, 2)

    return {
        "answer": response["answer"],
        "sources": sources,
        "confidence": response["confidence"],
        "retrieved_chunks": len(context_chunks),
        "response_time": response_time + response["latency"],
        "prompt": prompt,
        "token_usage": response["token_usage"],
    }

from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
try:
    from groq import Groq
except ImportError:  # dependency is optional until Groq-backed generation is used
    Groq = None

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class LLMService:
    """Production-ready Groq-backed LLM service for RAG generation."""

    def __init__(self, api_key: str | None = None, model: str = "llama-3.1-8b-instant") -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model
        self.client = Groq(api_key=self.api_key) if self.api_key and Groq is not None else None

    def _build_system_prompt(self) -> str:
        return (
            "You are a grounded enterprise assistant. "
            "Use only the retrieved context provided by the user. "
            "Never invent facts or answer without evidence. "
            "If the context is insufficient, reply exactly: "
            '"I could not find enough information in the uploaded documents."'
        )

    def generate(self, prompt: str, *, temperature: float = 0.2) -> dict[str, Any]:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is not configured")

        started_at = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        return {
            "answer": content,
            "sources": [],
            "confidence": "high" if content else "low",
            "latency": latency_ms,
            "token_usage": {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            },
        }

    def chat(self, messages: list[dict[str, str]], *, temperature: float = 0.2) -> dict[str, Any]:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is not configured")

        started_at = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        return {
            "answer": content,
            "sources": [],
            "confidence": "high" if content else "low",
            "latency": latency_ms,
            "token_usage": {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            },
        }

    def stream(self, prompt: str, *, temperature: float = 0.2) -> Any:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is not configured")

        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            stream=True,
        )

    def health_check(self) -> dict[str, Any]:
        return {
            "status": "ok" if self.client is not None else "not_configured",
            "model": self.model,
            "provider": "groq",
        }

from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
from loguru import logger

try:
    from groq import Groq
except ImportError:  # pragma: no cover - optional dependency path
    Groq = None

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class GroqService:
    """Dedicated Groq-backed RAG answer generator."""

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int | None = None) -> None:
        self.api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
        self.model = (model or os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()
        self.timeout = int(timeout or os.getenv("GROQ_TIMEOUT", "30"))
        self.client = Groq(api_key=self.api_key) if self.api_key and Groq is not None else None

    def _build_system_prompt(self) -> str:
        return (
            "You are the AI assistant for CustomerLens_AI. "
            "Answer the user's question using ONLY the information contained in the retrieved context. "
            "Do not use outside knowledge when the retrieved context does not support the answer. "
            "Do not simply copy one retrieved chunk. Synthesize across relevant chunks when useful. "
            "Do not dump raw PDF text or include OCR artifacts. "
            "Do not invent facts. "
            "If the retrieved context does not contain enough information to answer the question, say exactly: "
            "I couldn't find enough information in the uploaded documents to answer this question."
            "Keep the answer clear, concise, and natural."
        )

    def generate_answer(self, question: str, context: str) -> str:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is not configured")
        if not question.strip():
            raise ValueError("Question cannot be empty")
        if not context.strip():
            raise ValueError("Context cannot be empty")

        logger.info("Groq answer generation started")
        started_at = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {
                        "role": "user",
                        "content": (
                            f"USER QUESTION:\n{question}\n\n"
                            f"RETRIEVED CONTEXT:\n{context}\n\n"
                            "Generate the final answer."
                        ),
                    },
                ],
                temperature=0.2,
                timeout=self.timeout,
            )
        except Exception as exc:
            logger.exception("Groq generation failed")
            raise RuntimeError(f"Groq generation failed: {exc}") from exc

        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        content = (getattr(response.choices[0].message, "content", None) or "").strip()
        if not content:
            raise RuntimeError("Groq returned an empty response")
        logger.info("Groq answer generated successfully in {:.2f} ms", latency_ms)
        return content

    def health_check(self) -> dict[str, Any]:
        return {
            "status": "ok" if self.client is not None else "not_configured",
            "model": self.model,
            "provider": "groq",
        }

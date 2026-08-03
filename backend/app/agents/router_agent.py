from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any


class RouterAgent:
    """Intelligently routes a user query to Pandas, RAG, or a hybrid workflow."""

    def __init__(self) -> None:
        self.pandas_keywords = {
            "top",
            "rank",
            "customer",
            "revenue",
            "sales",
            "by",
            "compare",
            "trend",
            "analysis",
            "metric",
            "dataset",
            "table",
        }
        self.rag_keywords = {
            "document",
            "policy",
            "summarize",
            "article",
            "manual",
            "report",
            "complaint",
            "support",
            "context",
            "knowledge",
            "file",
            "upload",
        }
        self.hybrid_markers = {
            "and",
            "use",
            "combined",
            "with",
            "complaints",
            "churn",
            "why",
            "cause",
            "reason",
        }

    def detect_query_type(self, user_input: str) -> str:
        """Detect whether the request should use Pandas, RAG, or both."""
        text = user_input.lower()
        has_pandas = any(keyword in text for keyword in self.pandas_keywords)
        has_rag = any(keyword in text for keyword in self.rag_keywords)

        if has_pandas and has_rag:
            return "hybrid"

        if has_pandas:
            return "pandas"

        if has_rag:
            return "rag"

        if any(marker in text for marker in self.hybrid_markers) and ("customer" in text or "complaint" in text):
            return "hybrid"

        return "rag"

    async def route_query(self, user_input: str) -> dict[str, Any]:
        """Route the user input and return a structured response payload."""
        started_at = perf_counter()
        query_type = self.detect_query_type(user_input)

        if query_type == "pandas":
            pandas_result = await self._run_pandas_pipeline(user_input)
            response = {
                "query_type": "pandas",
                "answer": pandas_result["answer"],
                "sources": pandas_result["sources"],
                "confidence": pandas_result["confidence"],
                "response_time": round(perf_counter() - started_at, 3),
            }
            return response

        if query_type == "rag":
            rag_result = await self._run_rag_pipeline(user_input)
            response = {
                "query_type": "rag",
                "answer": rag_result["answer"],
                "sources": rag_result["sources"],
                "confidence": rag_result["confidence"],
                "response_time": round(perf_counter() - started_at, 3),
            }
            return response

        pandas_result, rag_result = await asyncio.gather(
            self._run_pandas_pipeline(user_input),
            self._run_rag_pipeline(user_input),
        )
        answer = self.merge_responses(pandas_result, rag_result)
        sources = list(dict.fromkeys([*pandas_result["sources"], *rag_result["sources"]]))
        confidence = self._merge_confidence(pandas_result["confidence"], rag_result["confidence"])

        return {
            "query_type": "hybrid",
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "response_time": round(perf_counter() - started_at, 3),
        }

    def merge_responses(self, pandas_result: dict[str, Any], rag_result: dict[str, Any]) -> str:
        """Combine Pandas and RAG answers into a single response."""
        sections: list[str] = []
        if pandas_result.get("answer"):
            sections.append(f"Structured analysis: {pandas_result['answer']}")
        if rag_result.get("answer"):
            sections.append(f"Document insights: {rag_result['answer']}")
        return "\n\n".join(sections) if sections else "No answer available."

    async def _run_pandas_pipeline(self, user_input: str) -> dict[str, Any]:
        await asyncio.sleep(0)
        return {
            "answer": f"Pandas pipeline placeholder for: {user_input}",
            "sources": ["structured_dataset"],
            "confidence": "high",
        }

    async def _run_rag_pipeline(self, user_input: str) -> dict[str, Any]:
        await asyncio.sleep(0)
        return {
            "answer": f"RAG pipeline placeholder for: {user_input}",
            "sources": ["document_chunks"],
            "confidence": "medium",
        }

    def _merge_confidence(self, pandas_confidence: str, rag_confidence: str) -> str:
        if pandas_confidence == "high" and rag_confidence == "high":
            return "high"
        if pandas_confidence == "high" or rag_confidence == "high":
            return "medium"
        return "low"

    async def route(self, user_input: str) -> str:
        """Compatibility helper returning the detected routing type."""
        return self.detect_query_type(user_input)

    def route_sync(self, user_input: str) -> str:
        """Synchronous compatibility helper for enterprise services."""
        return self.detect_query_type(user_input)

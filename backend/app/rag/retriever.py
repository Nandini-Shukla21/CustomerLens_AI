from __future__ import annotations

from typing import Any


class Retriever:
    """Placeholder retriever abstraction."""

    async def retrieve(self, query: str) -> list[dict[str, Any]]:
        return []

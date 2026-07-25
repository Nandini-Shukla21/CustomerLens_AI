from __future__ import annotations

from typing import Any

from fastapi import Request


def get_request_context(request: Request) -> dict[str, Any]:
    return {
        "request_id": request.headers.get("x-request-id", "n/a"),
        "path": request.url.path,
    }

from __future__ import annotations

from fastapi import HTTPException, status


class ServiceError(Exception):
    """Base exception for backend service-layer failures."""


class ResourceNotFoundError(ServiceError):
    """Raised when a requested resource cannot be found."""


class ValidationError(ServiceError):
    """Raised when request validation fails."""


def raise_http_error(status_code: int, detail: str) -> None:
    raise HTTPException(status_code=status_code, detail=detail)

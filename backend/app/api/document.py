from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

from app.dependencies import get_document_service
from app.services.document_service import DocumentService


router = APIRouter()


@router.post(
    "/upload/documents",
    response_model=dict[str, object],
)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    service: Annotated[
        DocumentService,
        Depends(get_document_service),
    ],
) -> dict[str, object]:
    """Upload a supported document and ingest it into the RAG pipeline."""

    return await service.ingest_document(file)


@router.get("")
async def list_documents(
    service: Annotated[
        DocumentService,
        Depends(get_document_service),
    ],
) -> list[dict[str, object]]:
    """Return all uploaded documents."""

    return service.list_documents()


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    service: Annotated[
        DocumentService,
        Depends(get_document_service),
    ],
) -> dict[str, object]:
    """Return metadata for one document."""

    try:
        return service.get_document(document_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    service: Annotated[
        DocumentService,
        Depends(get_document_service),
    ],
) -> FileResponse:
    """Download the original uploaded document."""

    try:
        document = service.get_document(document_id)
        file_path = service.get_document_path(document_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return FileResponse(
        path=file_path,
        filename=document["filename"],
        media_type="application/octet-stream",
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    service: Annotated[
        DocumentService,
        Depends(get_document_service),
    ],
) -> dict[str, object]:
    """Delete a document from storage."""

    try:
        document = service.delete_document(document_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "status": "success",
        "message": f'{document["filename"]} deleted successfully.',
        "document_id": document_id,
        "filename": document["filename"],
    }
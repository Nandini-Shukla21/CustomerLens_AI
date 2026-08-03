from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File

from app.dependencies import get_document_service
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/upload/document", response_model=dict[str, object])
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> dict[str, object]:
    """Upload a supported document and ingest it into the RAG pipeline."""
    return await service.ingest_document(file)

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.services.dataframe_manager import DataFrameManager


router = APIRouter()

manager = DataFrameManager()

# Folder where CSVService saves uploaded files.
UPLOAD_DIR = Path("./uploads")


# ============================================================
# LIST DATASETS
# ============================================================

@router.get("/")
async def list_datasets():
    """Return all currently managed datasets."""

    return manager.list_datasets()


# ============================================================
# DATASET DOWNLOAD
# IMPORTANT: Keep this BEFORE /{dataset_id}
# ============================================================

@router.get("/{dataset_id}/download")
async def download_dataset(dataset_id: str):
    """
    Download the original uploaded CSV file.
    """

    try:
        record = manager.get_dataset_metadata(dataset_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    # CSVService currently saves uploaded files to ./uploads
    file_path = UPLOAD_DIR / Path(record.filename).name

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Original dataset file was not found: "
                f"{file_path}"
            ),
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Dataset file is not available.",
        )

    return FileResponse(
        path=str(file_path),
        filename=record.filename,
        media_type="text/csv",
    )


# ============================================================
# DATASET DELETE
# ============================================================

@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset from memory and remove its uploaded CSV file.
    """

    # Get the record BEFORE deleting it because
    # DataFrameManager.delete_dataframe() currently returns None.
    try:
        record = manager.get_dataset_metadata(dataset_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    # Delete dataframe from memory.
    manager.delete_dataframe(dataset_id)

    # Delete physical CSV file.
    file_path = UPLOAD_DIR / Path(record.filename).name

    try:
        if file_path.exists():
            file_path.unlink()

    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Dataset was removed from memory, "
                f"but the uploaded file could not be deleted: {exc}"
            ),
        ) from exc

    return {
        "status": "success",
        "message": f"{record.filename} deleted successfully.",
        "dataset_id": dataset_id,
        "filename": record.filename,
    }


# ============================================================
# DATASET SUMMARY / PREVIEW
# IMPORTANT: This comes AFTER /download and /delete
# ============================================================

@router.get("/{dataset_id}")
async def dataset_summary(
    dataset_id: str,
    offset: int = 0,
    limit: int = Query(25, le=200),
    search: str = "",
):
    """
    Return dataset metadata and a paginated dataframe preview.
    """

    try:
        frame = manager.get_dataframe(dataset_id)
        record = manager.get_dataset_metadata(dataset_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search:
        mask = (
            frame.astype(str)
            .apply(
                lambda column: column.str.contains(
                    search,
                    case=False,
                    na=False,
                )
            )
            .any(axis=1)
        )

        frame = frame[mask]

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    preview_frame = frame.iloc[offset : offset + limit]

    # Replace NaN with None so the response is valid JSON.
    preview = (
        preview_frame.where(preview_frame.notna(), None)
        .to_dict(orient="records")
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "dataset_id": dataset_id,
        "filename": record.filename,
        "rows": record.row_count,
        "columns": record.column_count,
        "column_names": record.columns,
        "data_types": {
            str(k): str(v)
            for k, v in preview_frame.dtypes.items()
        },
        "missing_values": {
            str(k): int(v)
            for k, v in preview_frame.isna().sum().items()
        },
        "total_filtered": int(len(frame)),
        "offset": offset,
        "limit": limit,
        "preview": preview,
    }
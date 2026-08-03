from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from app.services.dataframe_manager import DataFrameManager

router = APIRouter()
manager = DataFrameManager()

@router.get("/")
async def list_datasets():
    return manager.list_datasets()

@router.get("/{dataset_id}")
async def dataset_summary(dataset_id: str, offset: int = 0, limit: int = Query(25, le=200), search: str = ""):
    try:
        frame = manager.get_dataframe(dataset_id)
        record = manager.get_dataset_metadata(dataset_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    if search:
        mask = frame.astype(str).apply(lambda column: column.str.contains(search, case=False, na=False)).any(axis=1)
        frame = frame[mask]
    preview = frame.iloc[offset:offset + limit].where(frame.notna(), None).to_dict(orient="records")
    return {
        "dataset_id": dataset_id, "filename": record.filename, "rows": record.row_count,
        "columns": record.column_count, "column_names": record.columns,
        "data_types": {str(k): str(v) for k, v in frame.dtypes.items()},
        "missing_values": {str(k): int(v) for k, v in frame.isna().sum().items()},
        "total_filtered": int(len(frame)), "offset": offset, "limit": limit, "preview": preview,
    }

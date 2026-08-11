from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import current_user
from app.services.analysis_service import analyze_dataset

router = APIRouter()


@router.get("/analytics")
def analytics(dataset_id: str | None = None, user: dict = Depends(current_user)):
    """Return dataset-driven analytics using the shared analysis service.

    If `dataset_id` is omitted, the most recent dataset for the user will be used
    by the underlying `load_dataset` call in the analysis service.
    """
    # analyze_dataset will raise if the dataset is not found; it returns a
    # structured payload containing `metrics`, `charts`, `detected`, etc.
    if not dataset_id:
        # analyze_dataset expects a dataset id; platform.load_dataset inside
        # it will raise if none exists. To preserve existing behaviour, we
        # attempt to find the most recent dataset id for the user.
        from app.core.storage import connection

        with connection() as conn:
            row = conn.execute(
                "SELECT id FROM datasets WHERE owner_id=? ORDER BY created_at DESC LIMIT 1",
                (user["sub"],),
            ).fetchone()

        if not row:
            return {
                "dataset_id": None,
                "records": 0,
                "metrics": {},
                "charts": [],
                "columns": [],
            }

        dataset_id = row["id"]

    return analyze_dataset(dataset_id, user["sub"])

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.core.security import current_user
from app.services.analysis_service import analyze_dataset

router = APIRouter()


@router.get("/")
def list_insights(dataset_id: str | None = None, user: dict = Depends(current_user)) -> List[dict[str, object]]:
    """Return AI-generated insights derived from the selected dataset.

    Insights are now factual and originate from the dataset via the shared
    analysis service. If no dataset is available, return an empty list.
    """
    if not dataset_id:
        from app.core.storage import connection

        with connection() as conn:
            row = conn.execute(
                "SELECT id FROM datasets WHERE owner_id=? ORDER BY created_at DESC LIMIT 1",
                (user["sub"],),
            ).fetchone()

        if not row:
            return []

        dataset_id = row["id"]

    analysis = analyze_dataset(dataset_id, user["sub"])
    return analysis.get("insights", [])

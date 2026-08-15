from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.core.security import current_user
from app.services.analysis_service import analyze_dataset


router = APIRouter()


@router.get("/")
def list_insights(
    dataset_id: str | None = None,
    user: dict = Depends(current_user),
) -> List[dict[str, object]]:
    """
    Return dataset-driven AI insights.

    If dataset_id is not supplied, the most recently
    uploaded dataset belonging to the current user is used.
    """

    if not dataset_id:
        from app.core.storage import connection

        with connection() as conn:
            row = conn.execute(
                """
                SELECT id
                FROM datasets
                WHERE owner_id=?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (user["sub"],),
            ).fetchone()

        if not row:
            return []

        dataset_id = row["id"]

    analysis = analyze_dataset(
        dataset_id,
        user["sub"],
    )

    return analysis.get("insights", [])
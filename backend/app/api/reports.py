from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import current_user
from app.core.storage import connection
from app.services.analysis_service import analyze_dataset

router = APIRouter()


@router.get("/reports/dashboard")
def report_dashboard(dataset_id: str | None = None, user: dict = Depends(current_user)):
    """Return a dataset-driven report overview using the shared analysis service."""
    with connection() as conn:
        rows = conn.execute(
            "SELECT id FROM datasets WHERE owner_id=? ORDER BY created_at DESC",
            (user["sub"],),
        ).fetchall()

    if not rows:
        return {
            "dataset_id": None,
            "datasets": 0,
            "total_customers": None,
            "revenue": None,
            "transactions": 0,
            "high_risk_customers": None,
            "predicted_churn": None,
            "ai_insights": [],
        }

    dataset_ids = [row["id"] for row in rows]

    if not dataset_id or dataset_id not in dataset_ids:
        dataset_id = dataset_ids[0]

    analysis = analyze_dataset(dataset_id, user["sub"])

    # Map analysis.metrics to the report shape, preserving availability semantics
    m = analysis.get("metrics", {})

    return {
        "dataset_id": dataset_id,
        "datasets": len(dataset_ids),
        "total_customers": m.get("unique_customers"),
        "revenue": m.get("revenue"),
        "transactions": m.get("records"),
        "high_risk_customers": m.get("fraud_count"),
        "predicted_churn": m.get("churn_rate"),
        "ai_insights": analysis.get("insights", []),
    }

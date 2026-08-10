from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.core.security import current_user
from app.core.storage import connection, decode_json

router = APIRouter()


def _get_user_id(user: Any) -> int:
    """
    Extract the authenticated user's ID.

    Supports both:
    - dictionary-like users
    - objects with an id attribute
    """
    if isinstance(user, dict):
        return int(user["id"])

    return int(user.id)


@router.get("/summary")
def home_summary(
    user: Any = Depends(current_user),
) -> dict[str, Any]:

    owner_id = _get_user_id(user)

    with connection() as conn:

        # ============================================================
        # DATASET SUMMARY
        # ============================================================

        dataset_rows = conn.execute(
            """
            SELECT
                id,
                filename,
                rows,
                columns,
                created_at
            FROM datasets
            WHERE owner_id = ?
            ORDER BY created_at DESC
            """,
            (owner_id,),
        ).fetchall()

        datasets = [
            {
                "id": row["id"],
                "filename": row["filename"],
                "rows": row["rows"],
                "columns": row["columns"],
                "created_at": row["created_at"],
            }
            for row in dataset_rows
        ]

        # ============================================================
        # DOCUMENT SUMMARY
        # ============================================================

        document_rows = conn.execute(
            """
            SELECT
                id,
                filename,
                checksum,
                indexed_at,
                created_at
            FROM documents
            WHERE owner_id = ?
            ORDER BY created_at DESC
            """,
            (owner_id,),
        ).fetchall()

        documents = [
            {
                "id": row["id"],
                "filename": row["filename"],
                "checksum": row["checksum"],
                "indexed_at": row["indexed_at"],
                "created_at": row["created_at"],
                "status": "indexed" if row["indexed_at"] else "uploaded",
            }
            for row in document_rows
        ]

        # ============================================================
        # CUSTOMER STATISTICS
        # ============================================================

        customer_stats = conn.execute(
            """
            SELECT
                COUNT(*) AS total_customers,
                COALESCE(SUM(revenue), 0) AS total_revenue,
                COALESCE(SUM(transactions), 0) AS total_transactions,
                COALESCE(AVG(ltv), 0) AS average_ltv,
                COALESCE(AVG(risk), 0) AS average_risk,
                COALESCE(AVG(churn), 0) AS average_churn
            FROM customers c
            INNER JOIN datasets d
                ON c.dataset_id = d.id
            WHERE d.owner_id = ?
            """,
            (owner_id,),
        ).fetchone()

        # ============================================================
        # PREDICTION STATISTICS
        # ============================================================

        prediction_stats = conn.execute(
            """
            SELECT
                COUNT(*) AS total_predictions,
                COALESCE(AVG(probability), 0) AS average_probability,
                COALESCE(AVG(confidence), 0) AS average_confidence
            FROM predictions p
            LEFT JOIN datasets d
                ON p.dataset_id = d.id
            WHERE d.owner_id = ?
            """,
            (owner_id,),
        ).fetchone()

        # ============================================================
        # INSIGHTS
        # ============================================================

        insight_rows = conn.execute(
            """
            SELECT
                id,
                dataset_id,
                title,
                description,
                priority,
                confidence,
                action,
                created_at
            FROM insights
            WHERE dataset_id IN (
                SELECT id
                FROM datasets
                WHERE owner_id = ?
            )
            ORDER BY created_at DESC
            LIMIT 6
            """,
            (owner_id,),
        ).fetchall()

        insights = [
            {
                "id": row["id"],
                "dataset_id": row["dataset_id"],
                "title": row["title"],
                "description": row["description"],
                "priority": row["priority"],
                "confidence": row["confidence"],
                "action": row["action"],
                "created_at": row["created_at"],
            }
            for row in insight_rows
        ]

        # ============================================================
        # RECENT ACTIVITY
        # ============================================================

        activity_rows = conn.execute(
            """
            SELECT
                id,
                action,
                entity_type,
                entity_id,
                entity_name,
                metadata_json,
                created_at
            FROM activity_log
            WHERE owner_id = ?
            ORDER BY created_at DESC
            LIMIT 12
            """,
            (owner_id,),
        ).fetchall()

        recent_activity = [
            {
                "id": row["id"],
                "action": row["action"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "entity_name": row["entity_name"],
                "metadata": decode_json(
                    row["metadata_json"],
                    {},
                ),
                "created_at": row["created_at"],
            }
            for row in activity_rows
        ]

        # ============================================================
        # UPLOAD STATISTICS
        # ============================================================

        upload_stats = conn.execute(
            """
            SELECT
                COUNT(*) AS total_uploads,
                COALESCE(SUM(size_bytes), 0) AS total_size_bytes
            FROM uploads
            WHERE owner_id = ?
            """,
            (owner_id,),
        ).fetchone()

        # ============================================================
        # UPLOAD ACTIVITY FOR CHART
        # ============================================================

        upload_chart_rows = conn.execute(
            """
            SELECT
                DATE(created_at) AS date,
                COUNT(*) AS count
            FROM uploads
            WHERE owner_id = ?
            GROUP BY DATE(created_at)
            ORDER BY date ASC
            LIMIT 14
            """,
            (owner_id,),
        ).fetchall()

        upload_chart = [
            {
                "date": row["date"],
                "count": row["count"],
            }
            for row in upload_chart_rows
        ]

        # ============================================================
        # DATASET SIZE CHART
        # ============================================================

        dataset_chart = [
            {
                "name": row["filename"],
                "rows": row["rows"],
                "columns": row["columns"],
            }
            for row in dataset_rows[:8]
        ]

    # ================================================================
    # RESPONSE
    # ================================================================

    return {
        "stats": {
            "datasets": len(datasets),
            "documents": len(documents),
            "customers": int(customer_stats["total_customers"] or 0),
            "revenue": float(customer_stats["total_revenue"] or 0),
            "transactions": float(
                customer_stats["total_transactions"] or 0
            ),
            "average_ltv": float(
                customer_stats["average_ltv"] or 0
            ),
            "average_risk": float(
                customer_stats["average_risk"] or 0
            ),
            "average_churn": float(
                customer_stats["average_churn"] or 0
            ),
            "predictions": int(
                prediction_stats["total_predictions"] or 0
            ),
            "average_prediction_probability": float(
                prediction_stats["average_probability"] or 0
            ),
            "average_prediction_confidence": float(
                prediction_stats["average_confidence"] or 0
            ),
            "total_uploads": int(
                upload_stats["total_uploads"] or 0
            ),
            "total_size_bytes": int(
                upload_stats["total_size_bytes"] or 0
            ),
        },

        "datasets": datasets,

        "documents": documents,

        "recent_activity": recent_activity,

        "insights": insights,

        "charts": {
            "uploads": upload_chart,
            "datasets": dataset_chart,
        },
    }
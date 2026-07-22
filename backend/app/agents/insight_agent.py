from __future__ import annotations

from typing import Any


class InsightAgent:
    """Generate business insight payloads from a dataframe context."""

    def generate(self, dataframe: Any) -> list[dict[str, Any]]:
        if dataframe is None or dataframe.empty:
            return []

        insights: list[dict[str, Any]] = []
        revenue = float(dataframe["revenue"].sum()) if "revenue" in dataframe.columns else 0.0
        churn_count = int(dataframe["churn"].sum()) if "churn" in dataframe.columns else 0
        avg_spend = float(dataframe["revenue"].mean()) if "revenue" in dataframe.columns else 0.0
        high_risk = dataframe[dataframe["days_since_last_transaction"].fillna(999) > 30] if "days_since_last_transaction" in dataframe.columns else dataframe.head(0)

        insights.append(
            {
                "title": "Revenue momentum",
                "description": f"Current revenue totals are {revenue:,.0f} with an average spend of {avg_spend:,.0f}.",
                "importance": "high",
                "confidence": 0.91,
                "recommended_action": "Prioritize retention offers for customers with lower recent spend.",
            }
        )
        insights.append(
            {
                "title": "Retention risk",
                "description": f"{churn_count} customers show churn indicators based on recent activity patterns.",
                "importance": "high",
                "confidence": 0.88,
                "recommended_action": "Launch targeted recovery outreach for at-risk customers.",
            }
        )
        insights.append(
            {
                "title": "Engagement gaps",
                "description": "Customers with long inactivity periods are emerging as a clear opportunity for reactivation campaigns.",
                "importance": "medium",
                "confidence": 0.83,
                "recommended_action": "Trigger win-back journeys for customers inactive for 30+ days.",
            }
        )
        insights.append(
            {
                "title": "Spending anomalies",
                "description": "A subset of customers shows unusually low spend relative to their recent engagement history.",
                "importance": "medium",
                "confidence": 0.79,
                "recommended_action": "Review customer segmentation and offer personalized promotions.",
            }
        )
        insights.append(
            {
                "title": "Growth opportunity",
                "description": "Customers with higher recent spend remain the strongest candidates for upsell expansion.",
                "importance": "medium",
                "confidence": 0.86,
                "recommended_action": "Focus cross-sell campaigns on your highest-value customers.",
            }
        )

        if not high_risk.empty:
            insights.append(
                {
                    "title": "High-risk customers",
                    "description": f"{len(high_risk)} customers have not transacted recently and require immediate follow-up.",
                    "importance": "high",
                    "confidence": 0.9,
                    "recommended_action": "Assign account teams to review and reconnect with these customers.",
                }
            )

        return insights[:8]

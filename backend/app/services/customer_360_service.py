from __future__ import annotations

from typing import Any


class Customer360Service:
    """Service-oriented aggregation layer for customer 360 dashboards."""

    async def build_customer_profile(self, customer_id: str) -> dict[str, Any]:
        """Create a dashboard-optimized customer profile payload."""
        profile = {
            "customer_id": customer_id,
            "profile": {
                "name": f"Customer {customer_id}",
                "segment": "Premium",
                "status": "Active",
                "tenure_months": 24,
                "region": "North America",
            },
            "recent_transactions": [
                {"id": "txn-001", "date": "2026-07-15", "amount": 129.99, "channel": "web"},
                {"id": "txn-002", "date": "2026-07-10", "amount": 89.50, "channel": "app"},
            ],
            "revenue": {
                "total": 15420.0,
                "monthly_avg": 643.0,
                "currency": "USD",
            },
            "segment": "Premium",
            "risk": {
                "level": "medium",
                "score": 0.42,
                "reason": "Recent decline in engagement",
            },
            "lifetime_value": {
                "value": 28100.0,
                "currency": "USD",
                "band": "High",
            },
            "churn_score": 0.36,
            "complaint_summary": {
                "count": 2,
                "trend": "decreasing",
                "themes": ["billing", "support delay"],
            },
            "ai_recommendation": {
                "action": "Offer retention incentive",
                "priority": "high",
                "rationale": "High-value customer with moderate churn risk.",
            },
        }
        return profile

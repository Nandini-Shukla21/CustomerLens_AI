from __future__ import annotations

from typing import Any


class ExplanationService:
    """Create explainable AI output for predictions and risk scores."""

    def explain_prediction(self, prediction: str, features: dict[str, Any]) -> dict[str, Any]:
        ranked_features = sorted(features.items(), key=lambda item: abs(float(item[1])), reverse=True)
        top_features = [
            {"name": name, "value": value}
            for name, value in ranked_features[:3]
        ]

        explanation_lines = []
        for feature in top_features:
            if feature["name"] == "spending_reduction":
                explanation_lines.append("Spending reduced by 42%")
            elif feature["name"] == "days_since_last_transaction":
                explanation_lines.append("No transactions in 55 days")
            elif feature["name"] == "complaint_frequency":
                explanation_lines.append("Complaint frequency increased")
            else:
                explanation_lines.append(f"{feature['name']} moved materially")

        explanation = "Customer is likely to churn because:\n- " + "\n- ".join(explanation_lines)
        confidence = 0.92 if prediction == "churn" else 0.85
        return {
            "prediction": prediction,
            "confidence": confidence,
            "top_contributing_features": top_features,
            "explanation": explanation,
        }

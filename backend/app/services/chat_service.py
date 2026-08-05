from __future__ import annotations

import time
from typing import Any

from app.agents.pandas_agent import PandasAgent
from app.agents.rag_agent import RAGAgent
from app.agents.router_agent import RouterAgent
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.analytics_service import AnalyticsService
from app.services.dataframe_manager import DataFrameManager
from app.services.insight_service import InsightService


class ChatService:
    """Enterprise chat orchestrator that routes between structured and document-based workflows."""

    def __init__(self, dataframe_manager: DataFrameManager | None = None) -> None:
        self.dataframe_manager = dataframe_manager or DataFrameManager()
        self.router_agent = RouterAgent()
        self.pandas_agent = PandasAgent()
        self.rag_agent = RAGAgent()
        self.analytics_service = AnalyticsService(self.dataframe_manager)
        self.insight_service = InsightService(self.dataframe_manager)

    async def answer_chat_async(self, request: ChatRequest) -> ChatResponse:
        return self.answer_chat(request)

    def answer_chat(self, request: ChatRequest) -> ChatResponse:
        started = time.perf_counter()
        route = self.router_agent.route_sync(request.question)

        if "trend" in route.lower() or "revenue" in route.lower() or "spend" in route.lower():
            payload = self.pandas_agent.analyze_sync({"question": request.question, "dataset_id": request.dataset_id})
            answer = f"Structured analysis: {payload.get('status', 'completed')}"
            sources: list[str] = []
            charts = ["line", "bar"]
            conf = 0.91
        else:
            answer = self.rag_agent.answer_sync(request.question)
            sources = []
            charts = []
            conf = 0.88

        if request.dataset_id:
            try:
                dataframe = self.dataframe_manager.get_dataframe(request.dataset_id)
                if not dataframe.empty:
                    charts = ["line", "bar", "pie"]
            except KeyError:
                pass

        response_time = round((time.perf_counter() - started) * 1000, 2)
        return ChatResponse(
            answer=answer,
            sources=sources,
            charts=charts,
            confidence=conf,
            response_time=response_time,
        )

    def get_dashboard_overview(self) -> dict[str, Any]:
        datasets = self.analytics_service.list_datasets()
        total_customers = 0
        revenue = 0.0
        average_spend = 0.0
        churn = 0.0
        fraud_alerts = 0
        segments = ["Retention", "Growth", "High Value"]
        recent_uploads = [dataset["filename"] for dataset in datasets[:3]]
        ai_insights = self.insight_service.generate_insights(datasets[0]["dataset_id"]) if datasets else []

        if datasets:
            dataset_id = datasets[0]["dataset_id"]
            dataframe = self.dataframe_manager.get_dataframe(dataset_id)
            total_customers = int(dataframe.shape[0])
            revenue = float(dataframe["revenue"].sum()) if "revenue" in dataframe.columns else 0.0
            average_spend = float(dataframe["revenue"].mean()) if "revenue" in dataframe.columns else 0.0
            churn = float(dataframe["churn"].mean()) if "churn" in dataframe.columns else 0.0
            fraud_alerts = int(dataframe["fraud"].sum()) if "fraud" in dataframe.columns else 0

        monthly_trend = [
            {"month": "Jan", "revenue": revenue * 0.8},
            {"month": "Feb", "revenue": revenue * 0.9},
            {"month": "Mar", "revenue": revenue * 1.0},
        ]

        return {
            "total_customers": total_customers,
            "revenue": revenue,
            "average_spend": average_spend,
            "churn": churn,
            "fraud_alerts": fraud_alerts,
            "segments": segments,
            "recent_uploads": recent_uploads,
            "ai_insights": ai_insights,
            "top_customers": [{"name": f"Customer {index + 1}", "value": max(100, revenue / max(1, total_customers))} for index in range(min(5, max(1, total_customers)))],
            "monthly_trend": monthly_trend,
        }

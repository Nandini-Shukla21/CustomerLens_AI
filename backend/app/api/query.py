from __future__ import annotations

from fastapi import APIRouter

from app.agents.router_agent import RouterAgent
from app.models.request_models import QueryRequest
from app.models.response_models import QueryResponse

router = APIRouter()
router_agent = RouterAgent()


@router.post("/", response_model=QueryResponse)
async def query_documents(request: QueryRequest) -> QueryResponse:
    """Route incoming queries through the intelligent router agent."""
    result = await router_agent.route_query(request.question)
    return QueryResponse(
        message=f"Resolved as {result['query_type']}",
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"],
        retrieved_chunks=len(result["sources"]),
        response_time=result["response_time"],
    )

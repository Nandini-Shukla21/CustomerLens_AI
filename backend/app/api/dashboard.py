from __future__ import annotations

from fastapi import APIRouter

from app.services.customer_360_service import Customer360Service
from app.services.dashboard_service import DashboardService
from app.config import settings

router = APIRouter()
customer_360_service = Customer360Service()


@router.get("/")
async def dashboard_summary() -> dict[str, object]:
    """Return live metrics calculated from uploaded datasets."""
    return DashboardService(settings).get_dashboard_overview()


@router.get("/customer/{customer_id}")
async def customer_profile(customer_id: str) -> dict[str, object]:
    """Return a dashboard-ready customer 360 payload."""
    return await customer_360_service.build_customer_profile(customer_id)

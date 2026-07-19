from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_analytics_service, get_dashboard_service
from app.models.response_models import DashboardResponse, DatasetListResponse, DatasetSummaryResponse
from app.services.analytics_service import AnalyticsService
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def dashboard_summary(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardResponse:
    """Return dashboard metrics through the service layer."""
    return service.get_dashboard_summary()


@router.get("/overview")
async def dashboard_overview(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> dict[str, object]:
    """Return a Recharts-ready overview payload."""
    return service.get_dashboard_overview()


@router.get("/datasets", response_model=list[DatasetListResponse])
async def list_datasets(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> list[DatasetListResponse]:
    """Return metadata for all uploaded datasets."""
    return [DatasetListResponse(**item) for item in service.list_datasets()]


@router.get("/dataset/{dataset_id}/summary", response_model=DatasetSummaryResponse)
async def dataset_summary(
    dataset_id: str,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> DatasetSummaryResponse:
    """Return analytical details for a specific dataset."""
    return DatasetSummaryResponse(**service.get_dataset_summary(dataset_id))

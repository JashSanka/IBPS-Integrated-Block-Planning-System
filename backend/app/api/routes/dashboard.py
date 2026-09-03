"""
API Router - Dashboard & Operational Overview.
"""

from fastapi import APIRouter
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["Dashboard"])


@router.get(
    "/dashboard",
    response_model=DashboardSummaryResponse,
    summary="Dashboard Summary & KPI Overview",
    description="Returns aggregate maintenance task counts, corridor block window statistics, and baseline-vs-optimized KPI deltas.",
)
def get_dashboard_summary():
    return DashboardService.get_dashboard_summary()

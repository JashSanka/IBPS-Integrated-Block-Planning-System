"""
API Router - Health & System Status.
"""

from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Mode Check",
    description="Returns service health, API version, and synthetic data mode verification.",
)
def get_health():
    return HealthResponse()

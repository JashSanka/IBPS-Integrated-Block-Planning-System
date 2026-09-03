"""API routes package."""

from app.api.routes.health import router as health_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.blocks import router as blocks_router
from app.api.routes.plans import router as plans_router
from app.api.routes.what_if import router as what_if_router
from app.api.routes.diagnostics import router as diagnostics_router
from app.api.routes.datasets import router as datasets_router

__all__ = [
    "health_router",
    "dashboard_router",
    "tasks_router",
    "blocks_router",
    "plans_router",
    "what_if_router",
    "diagnostics_router",
    "datasets_router",
]

"""
IBPS — Integrated Block Planning System
Main FastAPI Application & Server Entrypoint.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Add backend root to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import server_settings
from app.core.errors import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.api.routes import (
    health_router,
    dashboard_router,
    tasks_router,
    blocks_router,
    plans_router,
    what_if_router,
    diagnostics_router,
    datasets_router,
)
from app.services.state_service import StateService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ibps.server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes in-memory state and pre-computes deterministic baseline & optimized plans."""
    logger.info("Initializing IBPS Railway Optimization State...")
    state = StateService.get_instance()
    logger.info(
        f"IBPS State Loaded successfully ({len(state.tasks)} tasks, {len(state.blocks)} blocks, {len(state.trains)} trains)."
    )
    yield
    logger.info("IBPS Railway Optimization Service shutting down.")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="IBPS — Integrated Block Planning System API",
        description=(
            "AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways.\n\n"
            "**Permanent Positioning Notice:** *IBPS provides AI-assisted decision support for maintenance block planning. "
            "Final approval and override remain with authorized railway personnel.*"
        ),
        version=server_settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Include API Routers under /api
    prefix = server_settings.api_prefix
    app.include_router(health_router, prefix=prefix)
    app.include_router(dashboard_router, prefix=prefix)
    app.include_router(tasks_router, prefix=prefix)
    app.include_router(blocks_router, prefix=prefix)
    app.include_router(plans_router, prefix=prefix)
    app.include_router(what_if_router, prefix=prefix)
    app.include_router(diagnostics_router, prefix=prefix)
    app.include_router(datasets_router, prefix=prefix)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    print("Starting IBPS FastAPI Server on http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

"""
API Router - Solver Diagnostic Audit & Candidate Explainability.
"""

from fastapi import APIRouter
from app.schemas.diagnostics import DiagnosticsResponse
from app.services.diagnostic_service import DiagnosticService

router = APIRouter(tags=["Optimization Diagnostics"])


@router.get(
    "/plans/diagnostics",
    response_model=DiagnosticsResponse,
    summary="Solver Audit & Candidate Opportunity Diagnostic",
    description="Returns candidate pair feasibility tallies, rejection categories, exact objective term contributions, and block allocation summaries for SIH explainability.",
)
def get_diagnostics():
    return DiagnosticService.get_diagnostics()

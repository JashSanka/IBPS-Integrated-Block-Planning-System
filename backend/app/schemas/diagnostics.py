"""
Pydantic Schemas - Solver Diagnostics & Candidate Audit.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class DiagnosticsResponse(BaseModel):
    """Diagnostic audit payload for solver inspection and SIH judge explainability."""
    total_candidate_pairs: int
    feasible_pairs_count: int
    rejected_pairs_count: int
    rejected_reasons_tally: Dict[str, int]
    objective_contributions: Dict[str, float]
    blocks_used_count: int
    department_combinations_by_block: Dict[str, List[str]]
    unscheduled_tasks_diagnostics: Dict[str, List[str]]
    solver_wall_time_seconds: float
    human_in_the_loop_positioning: str = (
        "IBPS provides AI-assisted decision support for maintenance block planning. "
        "Final approval and override remain with authorized railway personnel."
    )

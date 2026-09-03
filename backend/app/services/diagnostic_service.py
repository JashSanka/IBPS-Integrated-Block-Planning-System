"""
Diagnostic Service - Extracts and Formats Solver Diagnostic Reports for Explainability.
"""

from typing import Dict, List, Any
from app.schemas.diagnostics import DiagnosticsResponse
from app.optimization.optimizer import BlockPlanOptimizer
from app.services.state_service import get_state


class DiagnosticService:
    @staticmethod
    def get_diagnostics() -> DiagnosticsResponse:
        state = get_state()
        
        # Run a diagnostic optimization pass if not already performed
        optimizer = BlockPlanOptimizer(state.tasks, state.blocks, state.trains, state.goods)
        if not state.optimized_plan:
            plan = optimizer.solve(enable_objective=True)
            state.optimized_plan = plan
        else:
            # Generate diagnostic report
            optimizer.solve(enable_objective=True)

        diag = optimizer.last_diagnostic_report
        if not diag:
            return DiagnosticsResponse(
                total_candidate_pairs=len(state.tasks) * len(state.blocks),
                feasible_pairs_count=0,
                rejected_pairs_count=0,
                rejected_reasons_tally={},
                objective_contributions={},
                blocks_used_count=0,
                department_combinations_by_block={},
                unscheduled_tasks_diagnostics={},
                solver_wall_time_seconds=0.0,
            )

        return DiagnosticsResponse(
            total_candidate_pairs=diag.total_candidate_pairs,
            feasible_pairs_count=diag.feasible_pairs_count,
            rejected_pairs_count=diag.rejected_pairs_count,
            rejected_reasons_tally=diag.rejected_reasons_tally,
            objective_contributions=diag.objective_contributions,
            blocks_used_count=len(diag.blocks_used),
            department_combinations_by_block=diag.department_combinations_by_block,
            unscheduled_tasks_diagnostics=diag.unscheduled_tasks_details,
            solver_wall_time_seconds=diag.solver_wall_time_seconds,
        )

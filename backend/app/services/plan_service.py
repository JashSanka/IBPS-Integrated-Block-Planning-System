"""
Plan Service - Generates baseline and CP-SAT optimized plans and comparative metrics.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.models import BlockPlan
from app.domain.enums import PlanHorizon
from app.config import AppConfig, OptimizationObjectiveWeights
from app.schemas.plans import (
    PlanGenerateRequest,
    PlanResponse,
    PlanComparisonResponse,
)
from app.schemas.common import MetricDetail
from app.optimization.baseline import BaselineScheduler
from app.optimization.optimizer import BlockPlanOptimizer
from app.services.state_service import get_state


class PlanService:
    @staticmethod
    def _to_plan_response(plan: BlockPlan, plan_type: str) -> PlanResponse:
        obj_val = plan.objective_breakdown.get("total_objective_value") if plan.objective_breakdown else None
        return PlanResponse(
            plan_id=plan.plan_id,
            plan_type=plan_type,
            horizon=plan.horizon,
            generated_at=plan.generated_at,
            solver_status=plan.solver_status,
            objective_value=obj_val,
            blocks_used=plan.blocks_used,
            scheduled_tasks_count=len(plan.scheduled_tasks),
            unscheduled_tasks_count=len(plan.unscheduled_tasks),
            scheduled_tasks=plan.scheduled_tasks,
            unscheduled_tasks=plan.unscheduled_tasks,
            metrics=plan.metrics,
            objective_breakdown=plan.objective_breakdown,
            warnings=plan.warnings,
        )

    @staticmethod
    def generate_baseline_plan(horizon: PlanHorizon = PlanHorizon.WEEKLY) -> PlanResponse:
        state = get_state()
        scheduler = BaselineScheduler(state.tasks, state.blocks, state.trains, state.goods)
        plan = scheduler.solve(horizon=horizon)
        state.evaluator.evaluate_plan(plan)
        state.baseline_plan = plan
        return PlanService._to_plan_response(plan, "baseline")

    @staticmethod
    def generate_optimized_plan(request: PlanGenerateRequest) -> PlanResponse:
        state = get_state()
        
        # Configure objective profile if requested
        cfg = AppConfig()
        if request.objective_profile == "high_safety":
            cfg.objective_weights = OptimizationObjectiveWeights(
                critical_completion_bonus=1000,
                unscheduled_critical_penalty=1500,
            )
        elif request.objective_profile == "high_traffic_penalty":
            cfg.objective_weights = OptimizationObjectiveWeights(
                train_disruption_penalty_multiplier=35,
                goods_traffic_penalty_multiplier=25,
            )
        
        enable_obj = request.objective_profile != "pure_csp"
        optimizer = BlockPlanOptimizer(state.tasks, state.blocks, state.trains, state.goods, config=cfg)
        plan = optimizer.solve(horizon=request.horizon, enable_objective=enable_obj)
        state.evaluator.evaluate_plan(plan)
        state.optimized_plan = plan
        return PlanService._to_plan_response(plan, "optimized")

    @staticmethod
    def get_latest_plan(plan_type: str = "optimized") -> Optional[PlanResponse]:
        state = get_state()
        if plan_type == "baseline":
            if not state.baseline_plan:
                PlanService.generate_baseline_plan()
            return PlanService._to_plan_response(state.baseline_plan, "baseline")
        else:
            if not state.optimized_plan:
                PlanService.generate_optimized_plan(PlanGenerateRequest())
            return PlanService._to_plan_response(state.optimized_plan, "optimized")

    @staticmethod
    def get_plan_comparison() -> PlanComparisonResponse:
        state = get_state()
        if not state.baseline_plan:
            PlanService.generate_baseline_plan()
        if not state.optimized_plan:
            PlanService.generate_optimized_plan(PlanGenerateRequest())

        baseline = state.baseline_plan
        optimized = state.optimized_plan
        comparisons = state.evaluator.compare_plans(baseline, optimized)

        metric_details = []
        for c in comparisons:
            label = "No change" if c.delta == 0.0 else f"{'+' if c.improvement_pct > 0 else ''}{c.improvement_pct:.1f}%"
            metric_details.append(MetricDetail(
                metric_name=c.metric_name,
                display_name=c.display_name,
                baseline_value=c.baseline_value,
                optimized_value=c.optimized_value,
                delta=c.delta,
                percentage_change=c.improvement_pct,
                unit=c.unit,
                higher_is_better=c.higher_is_better,
                label=label,
            ))

        return PlanComparisonResponse(
            baseline_plan_id=baseline.plan_id,
            optimized_plan_id=optimized.plan_id,
            baseline_metrics=baseline.metrics,
            optimized_metrics=optimized.metrics,
            comparisons=metric_details,
        )

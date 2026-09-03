"""
What-If Service - Handles Emergency Task Injection, Re-planning, and Structured Diff Computation.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from app.domain.models import MaintenanceTask, BlockPlan
from app.domain.enums import Department, Severity, TaskStatus, PlanHorizon
from app.schemas.what_if import (
    EmergencyTaskInput,
    WhatIfReplanRequest,
    WhatIfReplanResponse,
    ReplanDiffResponse,
)
from app.schemas.common import MetricDetail
from app.services.plan_service import PlanService
from app.optimization.optimizer import BlockPlanOptimizer
from app.metrics.evaluator import MetricsEvaluator
from app.services.state_service import get_state


class WhatIfService:
    @staticmethod
    def _parse_department(dept_str: str) -> Department:
        s = dept_str.strip().upper()
        if "S" in s and "T" in s:
            return Department.S_AND_T
        elif "TRD" in s or "OHE" in s or "TRACTION" in s:
            return Department.TRD
        return Department.ENGINEERING

    @staticmethod
    def _parse_severity(sev_str: str) -> Severity:
        s = sev_str.strip().upper()
        if "CRIT" in s or s in ("5", "4"):
            return Severity.CRITICAL
        elif "MAJ" in s or s == "3":
            return Severity.MAJOR
        elif "MIN" in s or s == "2":
            return Severity.MINOR
        return Severity.ROUTINE

    @staticmethod
    def replan_emergency_task(request: WhatIfReplanRequest) -> WhatIfReplanResponse:
        state = get_state()
        raw = request.task

        # Ensure base plan exists
        if not state.optimized_plan:
            PlanService.generate_optimized_plan(request=None)
        
        base_plan = state.optimized_plan
        base_t = state.blocks[0].start_time if state.blocks else datetime(2026, 9, 1, 0, 0)

        # Convert EmergencyTaskInput to domain MaintenanceTask
        dept = WhatIfService._parse_department(raw.department)
        sev = WhatIfService._parse_severity(raw.severity)
        
        emergency_task = MaintenanceTask(
            task_id=raw.task_id or f"EMERGENCY-{datetime.now().strftime('%H%M%S')}",
            department=dept,
            asset_id=raw.asset_id or f"AST-{raw.corridor_id[:3]}-EM",
            asset_type=raw.asset_type or "RAIL_TRACK",
            corridor_id=raw.corridor_id,
            location=raw.location or "KM 100/0",
            defect_type=raw.defect_type or "EMERGENCY_DEFECT",
            severity=sev,
            criticality=float(raw.criticality),
            safety_risk=float(raw.safety_risk),
            overdue_days=0,
            estimated_duration_min=int(raw.duration_minutes),
            crew_required=int(raw.crew_required),
            resource_requirements=["EMERGENCY_TOOLS"],
            incompatible_tasks=raw.incompatible_tasks,
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=float(raw.traffic_criticality),
        )

        # Score emergency task
        state.priority_engine.score_task(emergency_task)

        # Combine task pool
        tasks_with_emergency = [t for t in state.tasks if t.task_id != emergency_task.task_id] + [emergency_task]

        # Pin existing schedule assignments for plan stability
        pinned_map = {st.task_id: st.block_id for st in base_plan.scheduled_tasks}

        # Solve CP-SAT re-plan
        replan_optimizer = BlockPlanOptimizer(tasks_with_emergency, state.blocks, state.trains, state.goods)
        replan_plan = replan_optimizer.solve(horizon=PlanHorizon.WEEKLY, enable_objective=True, pinned_assignments=pinned_map)

        # Evaluate re-planned metrics
        evaluator_replan = MetricsEvaluator(tasks_with_emergency, state.blocks, state.trains, state.goods)
        evaluator_replan.evaluate_plan(replan_plan)

        # Compute structured diff
        diff_domain = replan_optimizer.compute_replan_diff(base_plan, replan_plan, emergency_task_id=emergency_task.task_id)

        # Compute KPI impact deltas
        comparisons = evaluator_replan.compare_plans(base_plan, replan_plan)
        metric_deltas = []
        for c in comparisons:
            label = "No change" if c.delta == 0.0 else f"{'+' if c.improvement_pct > 0 else ''}{c.improvement_pct:.1f}%"
            metric_deltas.append(MetricDetail(
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

        diff_response = ReplanDiffResponse(
            previous_plan_id=diff_domain.previous_plan_id,
            new_plan_id=diff_domain.new_plan_id,
            emergency_task_id=diff_domain.emergency_task_id,
            tasks_added=diff_domain.tasks_added,
            tasks_moved=diff_domain.tasks_moved,
            tasks_displaced=diff_domain.tasks_displaced,
            tasks_unchanged=diff_domain.tasks_unchanged,
            metric_deltas=metric_deltas,
        )

        return WhatIfReplanResponse(
            status="replanned",
            before=PlanService._to_plan_response(base_plan, "optimized"),
            after=PlanService._to_plan_response(replan_plan, "replanned_optimized"),
            diff=diff_response,
            kpi_impact=metric_deltas,
        )

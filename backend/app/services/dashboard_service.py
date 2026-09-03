"""
Dashboard Service - Aggregates system metrics, task counts, block usage, and KPI deltas.
"""

from typing import List, Dict, Any
from datetime import datetime

from app.schemas.dashboard import (
    DashboardSummaryResponse,
    TaskDashboardSummary,
    BlockDashboardSummary,
)
from app.schemas.common import MetricDetail
from app.domain.enums import PriorityBand
from app.services.state_service import get_state


class DashboardService:
    @staticmethod
    def get_dashboard_summary() -> DashboardSummaryResponse:
        state = get_state()
        tasks = state.tasks
        blocks = state.blocks
        baseline = state.baseline_plan
        optimized = state.optimized_plan

        # Task breakdown
        total_tasks = len(tasks)
        critical_tasks = sum(1 for t in tasks if t.priority_band == PriorityBand.CRITICAL)
        high_tasks = sum(1 for t in tasks if t.priority_band == PriorityBand.HIGH)
        medium_tasks = sum(1 for t in tasks if t.priority_band == PriorityBand.MEDIUM)
        routine_tasks = sum(1 for t in tasks if t.priority_band == PriorityBand.ROUTINE)

        scheduled_baseline = len(baseline.scheduled_tasks) if baseline else 0
        scheduled_optimized = len(optimized.scheduled_tasks) if optimized else 0
        unscheduled_optimized = len(optimized.unscheduled_tasks) if optimized else 0

        task_summary = TaskDashboardSummary(
            total=total_tasks,
            critical=critical_tasks,
            high=high_tasks,
            medium=medium_tasks,
            routine=routine_tasks,
            scheduled_baseline=scheduled_baseline,
            scheduled_optimized=scheduled_optimized,
            unscheduled_optimized=unscheduled_optimized,
        )

        # Block breakdown
        block_summary = BlockDashboardSummary(
            available=len(blocks),
            used_baseline=len(baseline.blocks_used) if baseline else 0,
            used_optimized=len(optimized.blocks_used) if optimized else 0,
            total_possession_hours_baseline=baseline.metrics.total_block_hours if baseline else 0.0,
            total_possession_hours_optimized=optimized.metrics.total_block_hours if optimized else 0.0,
        )

        # Comparative metrics
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

        departments = sorted(list({t.department.value for t in tasks}))
        corridors = sorted(list({t.corridor_id for t in tasks}))

        return DashboardSummaryResponse(
            active_dataset=state.active_dataset_type,
            tasks=task_summary,
            blocks=block_summary,
            metrics_summary=metric_details,
            departments=departments,
            corridors=corridors,
            last_plan_generated_at=optimized.generated_at if optimized else None,
        )

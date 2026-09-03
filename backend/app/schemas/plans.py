"""
Pydantic Schemas - Plan Generation, Optimization Runs, and Comparisons.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from app.domain.enums import PlanHorizon, SolverStatus
from app.domain.models import ScheduledTask, PlanMetrics
from app.schemas.common import MetricDetail


class PlanGenerateRequest(BaseModel):
    """Payload to trigger an optimization or baseline planning run."""
    horizon: PlanHorizon = Field(default=PlanHorizon.WEEKLY, description="Planning time horizon")
    objective_profile: str = Field(
        default="balanced",
        description="Objective weighting profile: 'balanced', 'high_safety', 'high_traffic_penalty', 'pure_csp'"
    )


class PlanResponse(BaseModel):
    """Plan generation output payload."""
    plan_id: str
    plan_type: str = Field(..., description="'baseline' or 'optimized'")
    horizon: PlanHorizon
    generated_at: datetime
    solver_status: SolverStatus
    objective_value: Optional[float] = None
    blocks_used: List[str]
    scheduled_tasks_count: int
    unscheduled_tasks_count: int
    scheduled_tasks: List[ScheduledTask]
    unscheduled_tasks: List[str]
    metrics: PlanMetrics
    objective_breakdown: Optional[Dict[str, float]] = None
    warnings: List[str] = Field(default_factory=list)


class PlanComparisonResponse(BaseModel):
    """Side-by-side comparison between fragmented baseline and IBPS optimized plan."""
    baseline_plan_id: str
    optimized_plan_id: str
    baseline_metrics: PlanMetrics
    optimized_metrics: PlanMetrics
    comparisons: List[MetricDetail]
    human_in_the_loop_positioning: str = (
        "IBPS provides AI-assisted decision support for maintenance block planning. "
        "Final approval and override remain with authorized railway personnel."
    )

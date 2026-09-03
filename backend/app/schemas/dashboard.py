"""
Pydantic Schemas - Dashboard & Overview Aggregates.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from app.schemas.common import MetricDetail


class TaskDashboardSummary(BaseModel):
    """Aggregate statistics of maintenance tasks."""
    total: int = Field(..., description="Total maintenance tasks in active scope")
    critical: int = Field(..., description="Number of CRITICAL priority band tasks")
    high: int = Field(..., description="Number of HIGH priority band tasks")
    medium: int = Field(..., description="Number of MEDIUM priority band tasks")
    routine: int = Field(..., description="Number of ROUTINE priority band tasks")
    scheduled_baseline: int = Field(..., description="Tasks scheduled by siloed baseline")
    scheduled_optimized: int = Field(..., description="Tasks scheduled by CP-SAT optimizer")
    unscheduled_optimized: int = Field(..., description="Tasks left unscheduled by CP-SAT")


class BlockDashboardSummary(BaseModel):
    """Aggregate statistics of corridor block windows."""
    available: int = Field(..., description="Total available track possession windows")
    used_baseline: int = Field(..., description="Block windows activated by baseline")
    used_optimized: int = Field(..., description="Block windows activated by CP-SAT")
    total_possession_hours_baseline: float = Field(..., description="Total closure hours in baseline")
    total_possession_hours_optimized: float = Field(..., description="Total closure hours in CP-SAT")


class DashboardSummaryResponse(BaseModel):
    """Top-level dashboard summary payload for the frontend."""
    data_badge: str = Field(
        default="SYNTHETIC / DEMO DATA ONLY — ARCHITECTURAL PROTOTYPE",
        description="Persistent transparency badge"
    )
    positioning_statement: str = Field(
        default="IBPS provides AI-assisted decision support for maintenance block planning. Final approval and override remain with authorized railway personnel.",
        description="Decision-support disclaimer"
    )
    active_dataset: str = Field(..., description="Active dataset identifier (e.g. demo_fixture)")
    tasks: TaskDashboardSummary
    blocks: BlockDashboardSummary
    metrics_summary: List[MetricDetail]
    departments: List[str]
    corridors: List[str]
    last_plan_generated_at: Optional[datetime] = None

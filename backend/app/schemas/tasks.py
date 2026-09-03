"""
Pydantic Schemas - Maintenance Tasks & Explainable Feasibility.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from app.domain.enums import Department, Severity, PriorityBand, TaskStatus


class TaskItemResponse(BaseModel):
    """UI-consumable task item schema."""
    task_id: str
    department: Department
    asset_id: str
    asset_type: str
    corridor_id: str
    location: str
    defect_type: str
    severity: Severity
    criticality: float
    safety_risk: float
    overdue_days: int
    estimated_duration_min: int
    crew_required: int
    resource_requirements: List[str]
    precedence: List[str]
    incompatible_tasks: List[str]
    earliest_start: datetime
    deadline: datetime
    status: TaskStatus
    traffic_criticality: float
    priority_score: Optional[float] = None
    priority_band: Optional[PriorityBand] = None
    score_breakdown: Optional[Dict[str, float]] = None
    scheduled_block_id: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    assignment_explanation: Optional[str] = None


class CandidateFeasibilityItem(BaseModel):
    """Structured feasibility report for a candidate block window."""
    block_id: str
    corridor_id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    feasible: bool
    reasons: List[str]


class TaskDetailResponse(BaseModel):
    """Detailed explainability view for a single maintenance task."""
    task: TaskItemResponse
    feasible_blocks_count: int
    feasible_blocks: List[str]
    candidate_evaluations: List[CandidateFeasibilityItem]
    precedence_tasks_details: List[Dict[str, Any]]
    incompatible_tasks_details: List[Dict[str, Any]]
    current_scheduled_block: Optional[Dict[str, Any]] = None

"""
Pydantic Schemas - Corridor Block Windows & Utilization.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from app.domain.enums import Department, TrafficDensity, TrainType, Direction


class BlockTaskAssignmentSummary(BaseModel):
    """Summary of a maintenance task scheduled in a block window."""
    task_id: str
    department: Department
    defect_type: str
    asset_id: str
    priority_score: float
    priority_band: str
    crew_required: int
    estimated_duration_min: int
    scheduled_start: datetime
    scheduled_end: datetime
    explanation: str


class BlockTrainImpactSummary(BaseModel):
    """Timetabled train overlapping or conflicting with a block window."""
    train_id: str
    train_type: TrainType
    direction: Direction
    start_time: datetime
    end_time: datetime
    operational_priority: int
    disruption_penalty: float
    is_hard_conflict: bool


class BlockFreightImpactSummary(BaseModel):
    """Freight traffic forecast for the corridor during block window."""
    time_window: str
    expected_goods_trains: int
    probability: float
    traffic_density: TrafficDensity


class BlockItemResponse(BaseModel):
    """Summary representation of a block possession window."""
    block_id: str
    corridor_id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    duration_hours: float
    available_capacity: int
    resource_capacity: int
    safety_constraints: List[str]
    permitted_departments: List[Department]
    traffic_density: TrafficDensity
    used_slots: int
    used_crew: int
    slot_utilization_pct: float
    crew_utilization_pct: float
    assigned_departments: List[Department]
    is_multi_department_clubbed: bool
    scheduled_tasks_count: int
    train_disruption_cost: float


class BlockDetailResponse(BaseModel):
    """Comprehensive detail for a single corridor block window."""
    block: BlockItemResponse
    assigned_tasks: List[BlockTaskAssignmentSummary]
    train_conflicts: List[BlockTrainImpactSummary]
    freight_forecasts: List[BlockFreightImpactSummary]
    clubbing_status_description: str
    safety_clearance_notes: List[str]

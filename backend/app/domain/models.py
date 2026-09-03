"""
IBPS Domain Models
Core Pydantic data structures for tasks, train movements, block windows, candidates, plans, metrics, and what-if replan diffs.
"""

from datetime import datetime
from typing import Optional, Dict, List, Any, Set
from pydantic import BaseModel, Field

from app.domain.enums import (
    Department,
    Severity,
    PriorityBand,
    TaskStatus,
    TrainType,
    Direction,
    TrafficDensity,
    SolverStatus,
    PlanHorizon,
)


class MaintenanceTask(BaseModel):
    """Represents a maintenance request raised by Engineering, S&T, or TRD."""
    task_id: str
    department: Department
    asset_id: str
    asset_type: str
    corridor_id: str
    location: str
    defect_type: str
    severity: Severity
    criticality: float = Field(..., ge=0.0, le=100.0, description="Asset criticality 0-100")
    safety_risk: float = Field(..., ge=0.0, le=100.0, description="Safety hazard rating 0-100")
    overdue_days: int = Field(default=0, ge=0)
    estimated_duration_min: int = Field(..., gt=0)
    crew_required: int = Field(default=1, ge=1)
    resource_requirements: List[str] = Field(default_factory=list)
    precedence: List[str] = Field(default_factory=list, description="Task IDs that must complete before this task")
    incompatible_tasks: List[str] = Field(default_factory=list, description="Task IDs that cannot share the same block window due to physical/safety/equipment conflicts")
    earliest_start: datetime
    deadline: datetime
    status: TaskStatus = TaskStatus.PENDING
    traffic_criticality: float = Field(default=50.0, ge=0.0, le=100.0)
    
    # Priority Engine Computed Attributes
    priority_score: Optional[float] = None
    risk_score: Optional[float] = None
    priority_band: Optional[PriorityBand] = None
    score_breakdown: Optional[Dict[str, float]] = None


class TrainMovement(BaseModel):
    """Scheduled train operating on a corridor."""
    train_id: str
    corridor_id: str
    train_type: TrainType
    direction: Direction
    start_time: datetime
    end_time: datetime
    operational_priority: int = Field(..., ge=1, le=5, description="1 is highest priority e.g. Vande Bharat")
    disruption_penalty: float = Field(..., ge=0.0)


class GoodsForecast(BaseModel):
    """Forecasted freight traffic on a corridor."""
    corridor_id: str
    time_window: str
    start_time: datetime
    end_time: datetime
    expected_goods_trains: int = Field(default=1, ge=0)
    probability: float = Field(default=1.0, ge=0.0, le=1.0)
    traffic_density: TrafficDensity = TrafficDensity.MEDIUM


class BlockWindow(BaseModel):
    """Available or proposed track possession/maintenance window."""
    block_id: str
    corridor_id: str
    start_time: datetime
    end_time: datetime
    available_capacity: int = Field(default=3, ge=1, description="Max concurrent task slots")
    resource_capacity: int = Field(default=10, ge=1, description="Max crew/machine capacity")
    safety_constraints: List[str] = Field(default_factory=list)
    permitted_departments: List[Department] = Field(
        default_factory=lambda: [Department.ENGINEERING, Department.S_AND_T, Department.TRD]
    )
    traffic_density: TrafficDensity = TrafficDensity.MEDIUM

    @property
    def duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() / 60)

    @property
    def duration_hours(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 3600.0


class CandidateEvaluation(BaseModel):
    """Feasibility outcome for a (task, block) candidate pair."""
    task_id: str
    block_id: str
    feasible: bool
    reasons: List[str] = Field(default_factory=list)


class ScheduledTask(BaseModel):
    """Task assigned to a concrete block window in a generated plan."""
    task_id: str
    block_id: str
    scheduled_start: datetime
    scheduled_end: datetime
    status: TaskStatus = TaskStatus.SCHEDULED
    explanation: str = ""


class PlanMetrics(BaseModel):
    """Summary KPI metrics computed live for a block plan."""
    total_tasks: int
    scheduled_tasks_count: int
    unscheduled_tasks_count: int
    total_critical_tasks: int
    critical_tasks_completed: int
    total_priority_score: float
    completed_priority_score: float
    priority_score_completion_pct: float
    blocks_used_count: int
    total_block_hours: float
    train_conflicts_count: int
    total_train_disruption_penalty: float
    goods_traffic_penalty: float
    average_block_utilization_pct: float
    multi_department_clubbed_blocks_count: int
    simulated_asset_availability_pct: float


class MetricComparison(BaseModel):
    """Side-by-side metric comparison between Baseline and IBPS Optimized plan."""
    metric_name: str
    display_name: str
    baseline_value: float
    optimized_value: float
    delta: float
    improvement_pct: float
    unit: str
    higher_is_better: bool


class BlockPlan(BaseModel):
    """Result of an optimization or baseline planning run."""
    plan_id: str
    horizon: PlanHorizon
    generated_at: datetime
    scheduled_tasks: List[ScheduledTask]
    unscheduled_tasks: List[str]
    blocks_used: List[str]
    metrics: PlanMetrics
    warnings: List[str] = Field(default_factory=list)
    solver_status: SolverStatus
    objective_breakdown: Optional[Dict[str, float]] = None


class ReplanTaskChange(BaseModel):
    """Details of a task affected during what-if re-planning."""
    task_id: str
    action: str  # "ADDED", "MOVED", "DISPLACED", "UNCHANGED"
    previous_block_id: Optional[str] = None
    new_block_id: Optional[str] = None
    reason: str


class ReplanDiff(BaseModel):
    """Comprehensive difference report between previous plan and re-planned schedule."""
    previous_plan_id: str
    new_plan_id: str
    emergency_task_id: str
    tasks_added: List[ReplanTaskChange] = Field(default_factory=list)
    tasks_moved: List[ReplanTaskChange] = Field(default_factory=list)
    tasks_displaced: List[ReplanTaskChange] = Field(default_factory=list)
    tasks_unchanged: List[str] = Field(default_factory=list)
    metric_deltas: List[MetricComparison] = Field(default_factory=list)


class SolverDiagnosticReport(BaseModel):
    """Diagnostic audit report for solver and candidate generation inspection."""
    total_candidate_pairs: int
    feasible_pairs_count: int
    rejected_pairs_count: int
    rejected_reasons_tally: Dict[str, int]
    scheduled_tasks_count: int
    unscheduled_tasks_count: int
    unscheduled_tasks_details: Dict[str, List[str]]
    blocks_used: List[str]
    department_combinations_by_block: Dict[str, List[str]]
    objective_contributions: Dict[str, float]
    solver_wall_time_seconds: float

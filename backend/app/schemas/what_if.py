"""
Pydantic Schemas - What-If Scenario Modeling & Emergency Re-planning.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from app.domain.models import ReplanTaskChange
from app.schemas.plans import PlanResponse
from app.schemas.common import MetricDetail


class EmergencyTaskInput(BaseModel):
    """Payload to inject an emergency maintenance defect into the planning pipeline."""
    task_id: str = Field(default="EMERGENCY-ENG-999", description="Unique emergency task ID")
    department: str = Field(default="ENGINEERING", description="ENGINEERING, S&T, or TRD")
    asset_id: str = Field(default="TRK-KP-118", description="Asset identifier")
    asset_type: str = Field(default="RAIL_TRACK", description="Track/Signal/OHE asset class")
    corridor_id: str = Field(default="KYN-PUN", description="Corridor section ID")
    location: str = Field(default="KM 118/6", description="Kilometer marker")
    defect_type: str = Field(default="SUDDEN_TRANSVERSE_RAIL_CRACK", description="Defect description")
    severity: str = Field(default="CRITICAL", description="CRITICAL, MAJOR, MINOR, or ROUTINE")
    criticality: float = Field(default=100.0, ge=0.0, le=100.0, description="Asset criticality (0-100)")
    safety_risk: float = Field(default=100.0, ge=0.0, le=100.0, description="Safety hazard rating (0-100)")
    duration_minutes: int = Field(default=120, gt=0, description="Estimated duration in minutes")
    crew_required: int = Field(default=4, ge=1, description="Required crew count")
    traffic_criticality: float = Field(default=95.0, ge=0.0, le=100.0)
    incompatible_tasks: List[str] = Field(default_factory=list, description="Mutually exclusive task IDs")


class WhatIfReplanRequest(BaseModel):
    """Request payload to perform what-if emergency replanning."""
    task: EmergencyTaskInput = Field(..., description="Emergency defect task details")
    pinned_plan_id: Optional[str] = Field(default=None, description="Optional previous plan ID to soft-pin against")


class ReplanDiffResponse(BaseModel):
    """Detailed difference report between previous plan and re-planned schedule."""
    previous_plan_id: str
    new_plan_id: str
    emergency_task_id: str
    tasks_added: List[ReplanTaskChange]
    tasks_moved: List[ReplanTaskChange]
    tasks_displaced: List[ReplanTaskChange]
    tasks_unchanged: List[str]
    metric_deltas: List[MetricDetail]


class WhatIfReplanResponse(BaseModel):
    """Response payload for what-if replanning."""
    status: str = Field(default="replanned", description="Replan execution status")
    before: PlanResponse
    after: PlanResponse
    diff: ReplanDiffResponse
    kpi_impact: List[MetricDetail]

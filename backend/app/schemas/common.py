"""
Pydantic Schemas - Common & Shared Types for IBPS API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
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


class MetricDetail(BaseModel):
    """Normalized comparative metric representation for frontend consumption."""
    metric_name: str = Field(..., description="Machine-readable metric key")
    display_name: str = Field(..., description="Human-readable Indian Railways metric title")
    baseline_value: float = Field(..., description="Value under siloed baseline scheduling")
    optimized_value: float = Field(..., description="Value under IBPS CP-SAT optimization")
    delta: float = Field(..., description="Absolute change (optimized - baseline)")
    percentage_change: float = Field(..., description="Percentage improvement or change")
    unit: str = Field(..., description="Measurement unit (e.g. tasks, hrs, %)")
    higher_is_better: bool = Field(..., description="Direction of optimization")
    label: str = Field(..., description="Formatted change label (e.g. '+22.9%' or 'No change')")

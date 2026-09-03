"""Schemas package."""

from app.schemas.common import MetricDetail
from app.schemas.health import HealthResponse
from app.schemas.dashboard import (
    TaskDashboardSummary,
    BlockDashboardSummary,
    DashboardSummaryResponse,
)
from app.schemas.tasks import (
    TaskItemResponse,
    CandidateFeasibilityItem,
    TaskDetailResponse,
)
from app.schemas.blocks import (
    BlockItemResponse,
    BlockDetailResponse,
    BlockTaskAssignmentSummary,
    BlockTrainImpactSummary,
    BlockFreightImpactSummary,
)
from app.schemas.plans import (
    PlanGenerateRequest,
    PlanResponse,
    PlanComparisonResponse,
)
from app.schemas.what_if import (
    EmergencyTaskInput,
    WhatIfReplanRequest,
    ReplanDiffResponse,
    WhatIfReplanResponse,
)
from app.schemas.diagnostics import DiagnosticsResponse
from app.schemas.datasets import DatasetSwitchRequest, DatasetSummaryResponse

__all__ = [
    "MetricDetail",
    "HealthResponse",
    "TaskDashboardSummary",
    "BlockDashboardSummary",
    "DashboardSummaryResponse",
    "TaskItemResponse",
    "CandidateFeasibilityItem",
    "TaskDetailResponse",
    "BlockItemResponse",
    "BlockDetailResponse",
    "BlockTaskAssignmentSummary",
    "BlockTrainImpactSummary",
    "BlockFreightImpactSummary",
    "PlanGenerateRequest",
    "PlanResponse",
    "PlanComparisonResponse",
    "EmergencyTaskInput",
    "WhatIfReplanRequest",
    "ReplanDiffResponse",
    "WhatIfReplanResponse",
    "DiagnosticsResponse",
    "DatasetSwitchRequest",
    "DatasetSummaryResponse",
]

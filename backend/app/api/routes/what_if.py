"""
API Router - What-If Scenario Modeling & Emergency Defect Re-planning.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.what_if import WhatIfReplanRequest, WhatIfReplanResponse
from app.services.what_if_service import WhatIfService

router = APIRouter(tags=["What-If Re-planning"])


@router.post(
    "/plans/what-if",
    response_model=WhatIfReplanResponse,
    status_code=status.HTTP_200_OK,
    summary="Inject Emergency Defect & Trigger Dynamic Re-plan",
    description="Injects an urgent maintenance defect into the scheduling pool, soft-pins existing commitments to avoid needless churn, and computes a structured before-vs-after diff.",
    responses={
        400: {"description": "Invalid emergency task payload"},
    },
)
def what_if_emergency_replan(request: WhatIfReplanRequest):
    if not request.task or not request.task.task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emergency task payload must include a valid task_id.",
        )
    return WhatIfService.replan_emergency_task(request)

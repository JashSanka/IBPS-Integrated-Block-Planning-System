"""
API Router - Maintenance Tasks & Explainable Feasibility.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.tasks import TaskItemResponse, TaskDetailResponse
from app.domain.enums import Department, PriorityBand, TaskStatus
from app.services.task_service import TaskService

router = APIRouter(tags=["Maintenance Tasks"])


@router.get(
    "/tasks",
    response_model=List[TaskItemResponse],
    summary="List Maintenance Tasks",
    description="Lists all maintenance requests raised by Engineering, S&T, and TRD with optional filtering.",
)
def list_tasks(
    department: Optional[Department] = Query(None, description="Filter by railway department (ENGINEERING, S&T, TRD)"),
    corridor: Optional[str] = Query(None, description="Filter by corridor ID (e.g. CSTM-KYN, KYN-PUN, NDLS-GZB)"),
    priority_band: Optional[PriorityBand] = Query(None, description="Filter by priority band (CRITICAL, HIGH, MEDIUM, ROUTINE)"),
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="Filter by status (SCHEDULED, UNSCHEDULED)"),
    search: Optional[str] = Query(None, description="Search keyword in defect type, asset ID, or location"),
):
    return TaskService.get_tasks(
        department=department,
        corridor=corridor,
        priority_band=priority_band,
        status=status_filter,
        search=search,
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskDetailResponse,
    summary="Task Detail & Feasibility Explainability",
    description="Returns detailed task metadata, multi-factor priority score breakdown, candidate block evaluations, and rejection reasons.",
    responses={
        404: {"description": "Task not found"},
    },
)
def get_task_detail(task_id: str):
    detail = TaskService.get_task_detail(task_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance task '{task_id}' was not found in active dataset.",
        )
    return detail

"""
API Router - Plan Generation, CP-SAT Optimization, and Baseline Comparisons.
"""

from typing import Optional
from fastapi import APIRouter, Query, status

from app.schemas.plans import (
    PlanGenerateRequest,
    PlanResponse,
    PlanComparisonResponse,
)
from app.domain.enums import PlanHorizon
from app.services.plan_service import PlanService

router = APIRouter(tags=["Block Planning & Optimization"])


@router.post(
    "/plans/baseline",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Fragmented Baseline Schedule",
    description="Executes the uncoordinated departmental first-fit greedy scheduler simulating current manual railway practice.",
)
def generate_baseline_plan(
    horizon: PlanHorizon = Query(PlanHorizon.WEEKLY, description="Planning time horizon"),
):
    return PlanService.generate_baseline_plan(horizon=horizon)


@router.post(
    "/plans/optimize",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Optimized Integrated Plan (CP-SAT)",
    description="Solves the cross-department block planning problem using Google OR-Tools CP-SAT constraint optimizer.",
)
def generate_optimized_plan(
    request: PlanGenerateRequest,
):
    return PlanService.generate_optimized_plan(request)


@router.get(
    "/plans/comparison",
    response_model=PlanComparisonResponse,
    summary="Compare Baseline vs IBPS Optimized Plan",
    description="Returns live side-by-side KPI metrics and calculated improvements (priority fulfillment, possession hours, clubbed blocks, availability proxy).",
)
def get_plan_comparison():
    return PlanService.get_plan_comparison()


@router.get(
    "/plans/latest",
    response_model=PlanResponse,
    summary="Get Latest Active Plan",
    description="Retrieves the most recently computed baseline or optimized plan.",
)
def get_latest_plan(
    plan_type: str = Query("optimized", description="'optimized' or 'baseline'"),
):
    return PlanService.get_latest_plan(plan_type=plan_type)

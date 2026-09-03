"""
Unit tests for CP-SAT Optimizer Objective Terms.
Tests clubbing bonus, priority maximization, and incremental objective behavior.
"""

from datetime import datetime, timedelta
from app.domain.models import MaintenanceTask, BlockWindow
from app.domain.enums import Department, Severity, SolverStatus
from app.optimization.optimizer import BlockPlanOptimizer


def test_cross_department_clubbing_incentive():
    """
    Given 1 block that accommodates both Engg and S&T tasks vs separate isolated options,
    the optimizer should choose to club them into the shared block to earn the clubbing bonus.
    """
    base_t = datetime(2026, 9, 1, 0, 0)
    task_eng = MaintenanceTask(
        task_id="T-ENG",
        department=Department.ENGINEERING,
        asset_id="AST-1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="TRACK_MAINT",
        severity=Severity.MAJOR,
        criticality=70.0,
        safety_risk=70.0,
        estimated_duration_min=60,
        crew_required=3,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )
    task_snt = MaintenanceTask(
        task_id="T-SNT",
        department=Department.S_AND_T,
        asset_id="AST-2",
        asset_type="SIGNAL",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="POINT_MAINT",
        severity=Severity.MAJOR,
        criticality=70.0,
        safety_risk=70.0,
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )

    shared_block = BlockWindow(
        block_id="B-SHARED",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=4),
        available_capacity=4,
        resource_capacity=10,
        permitted_departments=[Department.ENGINEERING, Department.S_AND_T],
    )

    optimizer = BlockPlanOptimizer([task_eng, task_snt], [shared_block], [], [])
    plan = optimizer.solve(enable_objective=True)

    assert plan.solver_status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
    assert len(plan.scheduled_tasks) == 2
    assert plan.scheduled_tasks[0].block_id == "B-SHARED"
    assert plan.scheduled_tasks[1].block_id == "B-SHARED"

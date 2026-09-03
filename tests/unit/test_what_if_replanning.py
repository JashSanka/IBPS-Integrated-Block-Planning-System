"""
Unit tests for What-If Emergency Re-planning and Structured Plan Diffing.
"""

from datetime import datetime, timedelta
from app.domain.models import MaintenanceTask, BlockWindow
from app.domain.enums import Department, Severity, SolverStatus
from app.optimization.optimizer import BlockPlanOptimizer


def test_what_if_emergency_task_insertion_and_displacement():
    base_t = datetime(2026, 9, 1, 0, 0)
    
    # 2 Tasks filling up a block with 8 crew capacity
    task_crit = MaintenanceTask(
        task_id="TASK-CRIT",
        department=Department.ENGINEERING,
        asset_id="AST-1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="RAIL_FRACTURE",
        severity=Severity.CRITICAL,
        criticality=95.0,
        safety_risk=95.0,
        overdue_days=7,
        estimated_duration_min=60,
        crew_required=4,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )
    task_routine = MaintenanceTask(
        task_id="TASK-ROUTINE",
        department=Department.TRD,
        asset_id="AST-2",
        asset_type="OHE",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="ROUTINE_GREASING",
        severity=Severity.ROUTINE,
        criticality=30.0,
        safety_risk=25.0,
        overdue_days=0,
        estimated_duration_min=60,
        crew_required=4,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )
    
    # Block with capacity of 8 crew (4 + 4 = 8, exactly full)
    block = BlockWindow(
        block_id="BLK-NIGHT-01",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=4),
        available_capacity=4,
        resource_capacity=8,
        safety_constraints=["POWER_BLOCK_AVAILABLE"],
        permitted_departments=[Department.ENGINEERING, Department.TRD],
    )

    # Initial plan
    optimizer1 = BlockPlanOptimizer([task_crit, task_routine], [block], [], [])
    plan1 = optimizer1.solve(enable_objective=True)

    assert len(plan1.scheduled_tasks) == 2

    # Now inject Emergency Task (needs 4 crew, max priority)
    emergency_task = MaintenanceTask(
        task_id="EMERGENCY-01",
        department=Department.ENGINEERING,
        asset_id="AST-EM",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 105",
        defect_type="EMERGENCY_RAIL_BREAK",
        severity=Severity.CRITICAL,
        criticality=100.0,
        safety_risk=100.0,
        overdue_days=0,
        estimated_duration_min=60,
        crew_required=4,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )

    tasks_replan = [task_crit, task_routine, emergency_task]
    optimizer2 = BlockPlanOptimizer(tasks_replan, [block], [], [])
    pinned = {st.task_id: st.block_id for st in plan1.scheduled_tasks}
    
    plan2 = optimizer2.solve(enable_objective=True, pinned_assignments=pinned)

    assert plan2.solver_status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
    
    # Emergency task and critical task must be scheduled; routine task displaced
    sch_ids = {st.task_id for st in plan2.scheduled_tasks}
    assert "EMERGENCY-01" in sch_ids
    assert "TASK-CRIT" in sch_ids
    assert "TASK-ROUTINE" not in sch_ids  # Displaced!

    # Verify structured replan diff
    diff = optimizer2.compute_replan_diff(plan1, plan2, emergency_task_id="EMERGENCY-01")
    assert any(tc.task_id == "EMERGENCY-01" and tc.action == "ADDED" for tc in diff.tasks_added)
    assert any(tc.task_id == "TASK-ROUTINE" and tc.action == "DISPLACED" for tc in diff.tasks_displaced)
    assert "TASK-CRIT" in diff.tasks_unchanged

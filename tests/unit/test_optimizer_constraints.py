"""
Comprehensive Unit Tests for CP-SAT Optimizer Hard Constraints.
Proves every single hard constraint is strictly enforced and NEVER violated to improve objective.
"""

from datetime import datetime, timedelta
import pytest
from app.domain.models import MaintenanceTask, BlockWindow, TrainMovement, GoodsForecast
from app.domain.enums import Department, Severity, SolverStatus, TrainType, Direction
from app.optimization.optimizer import BlockPlanOptimizer


def test_hard_constraint_at_most_once():
    """Prove a task is scheduled AT MOST ONCE even when multiple attractive blocks exist."""
    base_t = datetime(2026, 9, 1, 0, 0)
    task = MaintenanceTask(
        task_id="T-CRIT-1",
        department=Department.ENGINEERING,
        asset_id="AST-1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 10",
        defect_type="RAIL_CRACK",
        severity=Severity.CRITICAL,
        criticality=100.0,
        safety_risk=100.0,
        overdue_days=10,
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )
    blocks = [
        BlockWindow(
            block_id="B1",
            corridor_id="KYN-PUN",
            start_time=base_t + timedelta(hours=1),
            end_time=base_t + timedelta(hours=3),
            available_capacity=4,
            resource_capacity=10,
            permitted_departments=[Department.ENGINEERING],
        ),
        BlockWindow(
            block_id="B2",
            corridor_id="KYN-PUN",
            start_time=base_t + timedelta(hours=4),
            end_time=base_t + timedelta(hours=6),
            available_capacity=4,
            resource_capacity=10,
            permitted_departments=[Department.ENGINEERING],
        ),
    ]

    optimizer = BlockPlanOptimizer([task], blocks, [], [])
    plan = optimizer.solve(enable_objective=True)

    assert plan.solver_status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
    assigned_instances = [st for st in plan.scheduled_tasks if st.task_id == "T-CRIT-1"]
    assert len(assigned_instances) == 1


def test_hard_constraint_corridor_isolation():
    """Prove tasks CANNOT cross corridors even if other corridors have abundant open capacity."""
    base_t = datetime(2026, 9, 1, 0, 0)
    task = MaintenanceTask(
        task_id="T-CORR-1",
        department=Department.ENGINEERING,
        asset_id="AST-1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 10",
        defect_type="RAIL_CRACK",
        severity=Severity.CRITICAL,
        criticality=90.0,
        safety_risk=90.0,
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )
    block_other_corridor = BlockWindow(
        block_id="B-CSTM",
        corridor_id="CSTM-KYN",  # Different corridor
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=3),
        available_capacity=10,
        resource_capacity=20,
        permitted_departments=[Department.ENGINEERING],
    )

    optimizer = BlockPlanOptimizer([task], [block_other_corridor], [], [])
    plan = optimizer.solve(enable_objective=True)

    assert len(plan.scheduled_tasks) == 0
    assert "T-CORR-1" in plan.unscheduled_tasks


def test_hard_constraint_deadline_enforcement():
    """Prove tasks CANNOT be scheduled in block windows that end after their deadline."""
    base_t = datetime(2026, 9, 1, 0, 0)
    task = MaintenanceTask(
        task_id="T-DEADLINE-1",
        department=Department.ENGINEERING,
        asset_id="AST-1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 10",
        defect_type="RAIL_CRACK",
        severity=Severity.CRITICAL,
        criticality=95.0,
        safety_risk=95.0,
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=base_t,
        deadline=base_t + timedelta(hours=3),  # Deadline is 03:00
    )
    late_block = BlockWindow(
        block_id="B-LATE",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=4),  # Starts at 04:00 (past deadline)
        end_time=base_t + timedelta(hours=6),
        available_capacity=4,
        resource_capacity=10,
        permitted_departments=[Department.ENGINEERING],
    )

    optimizer = BlockPlanOptimizer([task], [late_block], [], [])
    plan = optimizer.solve(enable_objective=True)

    assert len(plan.scheduled_tasks) == 0
    assert "T-DEADLINE-1" in plan.unscheduled_tasks


def test_hard_constraint_resource_capacity():
    """
    Two critical tasks together exceed the block crew capacity.
    Solver must strictly respect resource capacity and NOT schedule both.
    """
    base_t = datetime(2026, 9, 1, 0, 0)
    task1 = MaintenanceTask(
        task_id="T-HEAVY-1",
        department=Department.ENGINEERING,
        asset_id="AST-1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 10",
        defect_type="RAIL_RENEWAL",
        severity=Severity.CRITICAL,
        criticality=90.0,
        safety_risk=90.0,
        overdue_days=5,
        estimated_duration_min=60,
        crew_required=7,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )
    task2 = MaintenanceTask(
        task_id="T-HEAVY-2",
        department=Department.ENGINEERING,
        asset_id="AST-2",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 12",
        defect_type="BALLAST_CLEANING",
        severity=Severity.CRITICAL,
        criticality=95.0,
        safety_risk=95.0,
        overdue_days=6,
        estimated_duration_min=60,
        crew_required=6,  # 7 + 6 = 13 > 10 capacity
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )
    block = BlockWindow(
        block_id="B-CAP-10",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=3),
        available_capacity=4,
        resource_capacity=10,
        permitted_departments=[Department.ENGINEERING],
    )

    optimizer = BlockPlanOptimizer([task1, task2], [block], [], [])
    plan = optimizer.solve(enable_objective=True)

    assert len(plan.scheduled_tasks) == 1
    total_crew = sum(optimizer.task_map[st.task_id].crew_required for st in plan.scheduled_tasks)
    assert total_crew <= 10


def test_hard_constraint_precedence():
    """Task B depends on Task A. Task B cannot be scheduled before Task A or if Task A is unscheduled."""
    base_t = datetime(2026, 9, 1, 0, 0)
    task_a = MaintenanceTask(
        task_id="TASK-A-ISOLATION",
        department=Department.TRD,
        asset_id="AST-A",
        asset_type="OHE",
        corridor_id="KYN-PUN",
        location="KM 50",
        defect_type="POWER_ISOLATION",
        severity=Severity.MAJOR,
        criticality=80.0,
        safety_risk=80.0,
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )
    task_b = MaintenanceTask(
        task_id="TASK-B-BRIDGE",
        department=Department.ENGINEERING,
        asset_id="AST-B",
        asset_type="BRIDGE",
        corridor_id="KYN-PUN",
        location="KM 50",
        defect_type="GIRDER_WORK",
        severity=Severity.CRITICAL,
        criticality=98.0,
        safety_risk=98.0,
        estimated_duration_min=60,
        crew_required=3,
        precedence=["TASK-A-ISOLATION"],
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )

    block1_early = BlockWindow(
        block_id="B-EARLY",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=3),
        available_capacity=4,
        resource_capacity=10,
        permitted_departments=[Department.ENGINEERING, Department.TRD],
        safety_constraints=["POWER_BLOCK_AVAILABLE"],
    )
    block2_late = BlockWindow(
        block_id="B-LATE",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=5),
        end_time=base_t + timedelta(hours=7),
        available_capacity=4,
        resource_capacity=10,
        permitted_departments=[Department.ENGINEERING, Department.TRD],
        safety_constraints=["POWER_BLOCK_AVAILABLE"],
    )

    optimizer = BlockPlanOptimizer([task_a, task_b], [block1_early, block2_late], [], [])
    plan = optimizer.solve(enable_objective=True)

    sch_map = {st.task_id: st for st in plan.scheduled_tasks}
    if "TASK-B-BRIDGE" in sch_map:
        assert "TASK-A-ISOLATION" in sch_map
        block_a = optimizer.block_map[sch_map["TASK-A-ISOLATION"].block_id]
        block_b = optimizer.block_map[sch_map["TASK-B-BRIDGE"].block_id]
        assert block_a.end_time <= block_b.start_time


def test_hard_constraint_incompatible_tasks():
    """
    Two tasks marked mutually incompatible (e.g. conflicting heavy machinery or spatial hazard)
    cannot be assigned to the same block window, even if crew capacity and slots allow it.
    """
    base_t = datetime(2026, 9, 1, 0, 0)
    task1 = MaintenanceTask(
        task_id="TASK-ENG-CRANE",
        department=Department.ENGINEERING,
        asset_id="AST-1",
        asset_type="CRANE",
        corridor_id="KYN-PUN",
        location="KM 60",
        defect_type="BOOM_CRANE_TURNOUT",
        severity=Severity.MAJOR,
        criticality=75.0,
        safety_risk=75.0,
        estimated_duration_min=60,
        crew_required=3,
        incompatible_tasks=["TASK-TRD-LIVE-TEST"],  # Mutually exclusive!
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )
    task2 = MaintenanceTask(
        task_id="TASK-TRD-LIVE-TEST",
        department=Department.TRD,
        asset_id="AST-2",
        asset_type="OHE",
        corridor_id="KYN-PUN",
        location="KM 60",
        defect_type="25KV_OHE_LIVE_TEST",
        severity=Severity.MAJOR,
        criticality=75.0,
        safety_risk=75.0,
        estimated_duration_min=60,
        crew_required=2,
        incompatible_tasks=["TASK-ENG-CRANE"],  # Mutually exclusive!
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )

    shared_block = BlockWindow(
        block_id="B-SHARED",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=4),
        available_capacity=4,
        resource_capacity=10,
        safety_constraints=["POWER_BLOCK_AVAILABLE"],
        permitted_departments=[Department.ENGINEERING, Department.TRD],
    )

    optimizer = BlockPlanOptimizer([task1, task2], [shared_block], [], [])
    plan = optimizer.solve(enable_objective=True)

    # Only one of the two incompatible tasks can be assigned to B-SHARED
    assigned_in_block = [st.task_id for st in plan.scheduled_tasks if st.block_id == "B-SHARED"]
    assert len(assigned_in_block) <= 1
    assert not ("TASK-ENG-CRANE" in assigned_in_block and "TASK-TRD-LIVE-TEST" in assigned_in_block)


def test_hard_constraint_safety_missing():
    """TRD task requiring POWER_BLOCK_AVAILABLE cannot be scheduled in a block lacking that safety condition."""
    base_t = datetime(2026, 9, 1, 0, 0)
    trd_task = MaintenanceTask(
        task_id="TASK-TRD-OHE",
        department=Department.TRD,
        asset_id="AST-OHE",
        asset_type="OHE_WIRE",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="OHE_WIRE_CHANGE",
        severity=Severity.CRITICAL,
        criticality=90.0,
        safety_risk=90.0,
        estimated_duration_min=60,
        crew_required=3,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )
    # Block lacks POWER_BLOCK_AVAILABLE
    no_power_block = BlockWindow(
        block_id="B-NO-POWER",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=4),
        available_capacity=4,
        resource_capacity=10,
        safety_constraints=["TRAFFIC_BLOCK_GRANTED"],  # NO POWER BLOCK!
        permitted_departments=[Department.ENGINEERING, Department.TRD],
    )

    optimizer = BlockPlanOptimizer([trd_task], [no_power_block], [], [])
    plan = optimizer.solve(enable_objective=True)

    assert len(plan.scheduled_tasks) == 0
    assert "TASK-TRD-OHE" in plan.unscheduled_tasks


def test_hard_constraint_train_conflict_prohibition():
    """A block overlapping with Priority-1 Vande Bharat train cannot be scheduled."""
    base_t = datetime(2026, 9, 1, 0, 0)
    task = MaintenanceTask(
        task_id="T-ENG",
        department=Department.ENGINEERING,
        asset_id="AST-1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="TRACK_CHECK",
        severity=Severity.MAJOR,
        criticality=70.0,
        safety_risk=70.0,
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )
    conflicting_block = BlockWindow(
        block_id="B-DAY-PEAK",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=11),
        end_time=base_t + timedelta(hours=13),
        available_capacity=4,
        resource_capacity=10,
        permitted_departments=[Department.ENGINEERING],
    )
    vande_bharat = TrainMovement(
        train_id="TRN-VB-22225",
        corridor_id="KYN-PUN",
        train_type=TrainType.VANDE_BHARAT,
        direction=Direction.DOWN,
        start_time=base_t + timedelta(hours=11, minutes=30),
        end_time=base_t + timedelta(hours=12, minutes=15),
        operational_priority=1,
        disruption_penalty=900.0,
    )

    optimizer = BlockPlanOptimizer([task], [conflicting_block], [vande_bharat], [])
    plan = optimizer.solve(enable_objective=True)

    assert len(plan.scheduled_tasks) == 0
    assert "B-DAY-PEAK" not in plan.blocks_used

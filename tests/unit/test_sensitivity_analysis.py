"""
Sensitivity Analysis Tests for CP-SAT Objective Weights.
Confirms optimizer stability and verifies that clubbing incentives never dominate critical safety priority.
"""

from datetime import datetime, timedelta
import copy
from app.domain.models import MaintenanceTask, BlockWindow
from app.domain.enums import Department, Severity, SolverStatus
from app.config import AppConfig, OptimizationObjectiveWeights
from app.optimization.optimizer import BlockPlanOptimizer


def test_objective_sensitivity_across_weight_profiles():
    base_t = datetime(2026, 9, 1, 0, 0)

    # 1 High-priority critical task (Engineering, prio 95, crew 4)
    # 2 Low-priority routine tasks (S&T and TRD, prio 25 each, crew 2 each)
    task_crit = MaintenanceTask(
        task_id="TASK-CRIT-ENG",
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
    task_snt = MaintenanceTask(
        task_id="TASK-ROUTINE-SNT",
        department=Department.S_AND_T,
        asset_id="AST-2",
        asset_type="SIGNAL",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="SIGNAL_CLEANING",
        severity=Severity.ROUTINE,
        criticality=25.0,
        safety_risk=20.0,
        overdue_days=0,
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )
    task_trd = MaintenanceTask(
        task_id="TASK-ROUTINE-TRD",
        department=Department.TRD,
        asset_id="AST-3",
        asset_type="OHE",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="OHE_GREASING",
        severity=Severity.ROUTINE,
        criticality=25.0,
        safety_risk=20.0,
        overdue_days=0,
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=2),
    )

    # Tight block with 4 crew capacity.
    # Choice: EITHER schedule 1 Critical Engg task (4 crew) OR schedule 2 Routine tasks together (S&T + TRD = 4 crew, clubbed).
    block = BlockWindow(
        block_id="BLK-TIGHT",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=4),
        available_capacity=4,
        resource_capacity=4,
        safety_constraints=["POWER_BLOCK_AVAILABLE"],
        permitted_departments=[Department.ENGINEERING, Department.S_AND_T, Department.TRD],
    )

    tasks = [task_crit, task_snt, task_trd]

    # Test under 3 different weight configurations:
    # 1. Default weights
    cfg_default = AppConfig()

    # 2. Heavy Clubbing Incentive (clubbing bonus 500)
    cfg_high_club = AppConfig(
        objective_weights=OptimizationObjectiveWeights(
            clubbing_bonus_per_extra_dept=500,
        )
    )

    # 3. Heavy Safety / Penalty profile
    cfg_heavy_safety = AppConfig(
        objective_weights=OptimizationObjectiveWeights(
            critical_completion_bonus=800,
            unscheduled_critical_penalty=1200,
        )
    )

    for cfg in [cfg_default, cfg_high_club, cfg_heavy_safety]:
        opt = BlockPlanOptimizer(tasks, [block], [], [], config=cfg)
        plan = opt.solve(enable_objective=True)
        
        assert plan.solver_status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
        sch_ids = [st.task_id for st in plan.scheduled_tasks]
        
        # In all sensible configurations, the CRITICAL task MUST win the resource capacity!
        assert "TASK-CRIT-ENG" in sch_ids, "Solver sacrificed critical safety task for routine clubbing!"

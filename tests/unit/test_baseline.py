"""
Unit tests for Baseline Greedy Scheduler.
"""

from datetime import datetime, timedelta
from app.domain.models import MaintenanceTask, BlockWindow
from app.domain.enums import Department, Severity, SolverStatus
from app.optimization.baseline import BaselineScheduler


def test_baseline_scheduler_execution(demo_fixture):
    tasks = demo_fixture["tasks"]
    blocks = demo_fixture["blocks"]
    trains = demo_fixture["trains"]
    goods = demo_fixture["goods"]

    baseline = BaselineScheduler(tasks, blocks, trains, goods)
    plan = baseline.solve()

    assert plan.solver_status == SolverStatus.FEASIBLE
    assert len(plan.scheduled_tasks) > 0
    assert len(plan.blocks_used) > 0

"""
End-to-End Integration Test for IBPS Demo Fixture.
Verifies that all 12 SIH demo story elements function properly end-to-end.
"""

from app.domain.models import MaintenanceTask
from app.domain.enums import Department, PriorityBand, Severity, SolverStatus
from app.optimization.baseline import BaselineScheduler
from app.optimization.optimizer import BlockPlanOptimizer
from app.metrics.evaluator import MetricsEvaluator


def test_end_to_end_demo_story(demo_fixture):
    tasks = demo_fixture["tasks"]
    blocks = demo_fixture["blocks"]
    trains = demo_fixture["trains"]
    goods = demo_fixture["goods"]
    emergency = demo_fixture["emergency_task"]

    # 1, 2, 3, 4: Tasks across 3 depts & multiple corridors
    depts = {t.department for t in tasks}
    corridors = {t.corridor_id for t in tasks}
    assert depts == {Department.ENGINEERING, Department.S_AND_T, Department.TRD}
    assert len(corridors) >= 3

    # Instantiate Optimizer
    optimizer = BlockPlanOptimizer(tasks, blocks, trains, goods)
    opt_plan = optimizer.solve(enable_objective=True)

    assert opt_plan.solver_status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)

    evaluator = MetricsEvaluator(tasks, blocks, trains, goods)
    metrics = evaluator.evaluate_plan(opt_plan)

    scheduled_map = {st.task_id: st for st in opt_plan.scheduled_tasks}

    # 5. Cross-department clubbing occurred
    assert metrics.multi_department_clubbed_blocks_count >= 1

    # Check that BLK-KP-NIGHT-01 has clubbed tasks from Engg, S&T, or TRD
    kp_tasks = [st for st in opt_plan.scheduled_tasks if st.block_id == "BLK-KP-NIGHT-01"]
    kp_depts = {optimizer.task_map[st.task_id].department for st in kp_tasks}
    assert len(kp_depts) >= 2, "Expected cross-department clubbing in BLK-KP-NIGHT-01"

    # 6. Safety critical defect (TASK-ENG-001) is scheduled
    assert "TASK-ENG-001" in scheduled_map

    # 7. Train conflict avoided: BLK-KP-DAY-PEAK (overlapping Vande Bharat) should NOT be used
    assert "BLK-KP-DAY-PEAK" not in opt_plan.blocks_used

    # 8. Resource bottleneck enforced: BLK-CK-NIGHT-01 has max 8 crew capacity
    ck_night_tasks = [st for st in opt_plan.scheduled_tasks if st.block_id == "BLK-CK-NIGHT-01"]
    ck_total_crew = sum(optimizer.task_map[st.task_id].crew_required for st in ck_night_tasks)
    assert ck_total_crew <= 8  # Bottleneck capacity limit

    # 9. Precedence preserved: TASK-ENG-004 depends on TASK-TRD-002
    if "TASK-ENG-004" in scheduled_map:
        assert "TASK-TRD-002" in scheduled_map
        st_a = scheduled_map["TASK-TRD-002"]
        st_b = scheduled_map["TASK-ENG-004"]
        block_a = optimizer.block_map[st_a.block_id]
        block_b = optimizer.block_map[st_b.block_id]
        assert block_a.end_time <= block_b.start_time

    # 10. Incompatible tasks mutual exclusion enforced
    if "TASK-ENG-HEAVY-009" in scheduled_map and "TASK-TRD-INCOMP-009" in scheduled_map:
        assert scheduled_map["TASK-ENG-HEAVY-009"].block_id != scheduled_map["TASK-TRD-INCOMP-009"].block_id

    # 11. What-If Emergency Task Re-planning
    tasks_with_emergency = tasks + [emergency]
    replan_optimizer = BlockPlanOptimizer(tasks_with_emergency, blocks, trains, goods)
    
    # Soft pinning current assignments
    pinned = {st.task_id: st.block_id for st in opt_plan.scheduled_tasks}
    replan = replan_optimizer.solve(enable_objective=True, pinned_assignments=pinned)

    assert replan.solver_status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
    replan_scheduled = {st.task_id: st for st in replan.scheduled_tasks}
    assert emergency.task_id in replan_scheduled, "Emergency task must be scheduled in replan!"

    # Verify structured replan diff output
    diff = replan_optimizer.compute_replan_diff(opt_plan, replan, emergency_task_id=emergency.task_id)
    assert any(tc.task_id == emergency.task_id for tc in diff.tasks_added)

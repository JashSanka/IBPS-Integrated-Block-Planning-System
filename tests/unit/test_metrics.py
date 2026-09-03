"""
Unit tests for MetricsEvaluator and Plan Comparison.
"""

from app.metrics.evaluator import MetricsEvaluator
from app.optimization.baseline import BaselineScheduler
from app.optimization.optimizer import BlockPlanOptimizer


def test_metrics_evaluator_live_computation(demo_fixture):
    tasks = demo_fixture["tasks"]
    blocks = demo_fixture["blocks"]
    trains = demo_fixture["trains"]
    goods = demo_fixture["goods"]

    evaluator = MetricsEvaluator(tasks, blocks, trains, goods)

    # Solve baseline and evaluate
    baseline_scheduler = BaselineScheduler(tasks, blocks, trains, goods)
    baseline_plan = baseline_scheduler.solve()
    b_metrics = evaluator.evaluate_plan(baseline_plan)

    assert b_metrics.total_tasks == len(tasks)
    assert b_metrics.scheduled_tasks_count + b_metrics.unscheduled_tasks_count == len(tasks)
    assert 0.0 <= b_metrics.simulated_asset_availability_pct <= 100.0

    # Solve optimizer and evaluate
    optimizer = BlockPlanOptimizer(tasks, blocks, trains, goods)
    opt_plan = optimizer.solve(enable_objective=True)
    o_metrics = evaluator.evaluate_plan(opt_plan)

    assert o_metrics.total_tasks == len(tasks)
    assert o_metrics.scheduled_tasks_count >= b_metrics.scheduled_tasks_count
    
    comparisons = evaluator.compare_plans(baseline_plan, opt_plan)
    assert len(comparisons) > 0
    for c in comparisons:
        assert c.metric_name is not None
        assert isinstance(c.delta, float)

"""
IBPS CLI Demonstration & Audit Runner.
Run via: python backend/app/cli.py [--audit]
"""

import sys
from pathlib import Path
import json
import argparse

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.data.generator import get_demo_fixture_data
from app.data.loader import export_demo_fixture, export_full_dataset
from app.scoring.priority_engine import PriorityEngine
from app.optimization.baseline import BaselineScheduler
from app.optimization.optimizer import BlockPlanOptimizer
from app.metrics.evaluator import MetricsEvaluator
from app.domain.enums import PlanHorizon


def main():
    parser = argparse.ArgumentParser(description="IBPS CLI Optimizer & Audit Demo")
    parser.add_argument("--audit", action="store_true", help="Print solver diagnostic report")
    args = parser.parse_args()

    print("=" * 92)
    print("  IBPS — INTEGRATED BLOCK PLANNING SYSTEM (PS 26027)")
    print("  Ministry of Railways | Smart India Hackathon Decision-Support Prototype")
    print("  [Badge: SYNTHETIC / DEMO DATA ONLY — ARCHITECTURAL PROTOTYPE]")
    print("=" * 92)

    export_demo_fixture()
    export_full_dataset()
    tasks, blocks, trains, goods, emergency_task = get_demo_fixture_data()

    print(f"[1/5] Loaded {len(tasks)} tasks, {len(blocks)} blocks, {len(trains)} trains.")

    # 2. Priority Scoring
    priority_engine = PriorityEngine()
    scored_tasks = priority_engine.score_all(tasks)
    critical_count = sum(1 for t in scored_tasks if t.priority_band and t.priority_band.value == "CRITICAL")
    print(f"[2/5] Priority Scoring complete -> Critical Tasks: {critical_count}")

    # 3. Baseline Plan
    baseline_scheduler = BaselineScheduler(tasks, blocks, trains, goods)
    baseline_plan = baseline_scheduler.solve(horizon=PlanHorizon.WEEKLY)
    print(f"[3/5] Fragmented Baseline Plan Generated: {len(baseline_plan.scheduled_tasks)} tasks scheduled.")

    # 4. CP-SAT Optimization
    optimizer = BlockPlanOptimizer(tasks, blocks, trains, goods)
    opt_plan = optimizer.solve(horizon=PlanHorizon.WEEKLY, enable_objective=True)
    print(f"[4/5] CP-SAT Optimizer Status: {opt_plan.solver_status.value} (Optimal Objective: {opt_plan.objective_breakdown.get('total_objective_value', 0):.1f})")

    # 5. Metrics & Comparison
    evaluator = MetricsEvaluator(tasks, blocks, trains, goods)
    evaluator.evaluate_plan(baseline_plan)
    evaluator.evaluate_plan(opt_plan)
    comparisons = evaluator.compare_plans(baseline_plan, opt_plan)

    print("\n" + "-" * 92)
    print(f"{'METRIC':<42} | {'BASELINE':<12} | {'IBPS (CP-SAT)':<15} | {'IMPROVEMENT':<14}")
    print("-" * 92)
    for c in comparisons:
        b_str = f"{c.baseline_value:.1f} {c.unit}"
        o_str = f"{c.optimized_value:.1f} {c.unit}"
        label = "No change" if c.delta == 0.0 else f"{'+' if c.improvement_pct > 0 else ''}{c.improvement_pct:.1f}%"
        print(f"{c.display_name:<42} | {b_str:<12} | {o_str:<15} | {label:<14}")
    print("-" * 92)

    # What-if replan
    tasks_with_emergency = tasks + [emergency_task]
    replan_optimizer = BlockPlanOptimizer(tasks_with_emergency, blocks, trains, goods)
    pinned_map = {st.task_id: st.block_id for st in opt_plan.scheduled_tasks}
    replan = replan_optimizer.solve(enable_objective=True, pinned_assignments=pinned_map)
    diff = replan_optimizer.compute_replan_diff(opt_plan, replan, emergency_task_id=emergency_task.task_id)

    print(f"\n[What-If Re-planning]: Emergency Task '{emergency_task.task_id}' accommodated.")
    for td in diff.tasks_displaced:
        print(f"  * Task '{td.task_id}' displaced to yield capacity for emergency work.")
    print("=" * 92)


if __name__ == "__main__":
    main()

"""
Naive Baseline Scheduler.
Simulates current fragmented, siloed railway maintenance scheduling:
- Departments (Engineering, S&T, TRD) plan sequentially and independently.
- Each department greedily takes the earliest available block window (First-Fit).
- No cross-department co-scheduling or multi-objective global optimization.
"""

from datetime import datetime
from typing import List, Dict, Set
import uuid

from app.domain.models import (
    MaintenanceTask,
    BlockWindow,
    TrainMovement,
    GoodsForecast,
    ScheduledTask,
    BlockPlan,
    PlanMetrics,
)
from app.domain.enums import Department, TaskStatus, SolverStatus, PlanHorizon
from app.optimization.candidate_model import CandidateModel
from app.scoring.priority_engine import PriorityEngine


class BaselineScheduler:
    """Greedy siloed baseline scheduler for benchmarking."""

    def __init__(
        self,
        tasks: List[MaintenanceTask],
        blocks: List[BlockWindow],
        trains: List[TrainMovement],
        goods: List[GoodsForecast],
    ):
        self.priority_engine = PriorityEngine()
        self.tasks = [t.model_copy(deep=True) for t in tasks]
        # Score tasks first so priority values are available
        self.priority_engine.score_all(self.tasks)
        
        self.blocks = sorted(blocks, key=lambda b: b.start_time)
        self.trains = trains
        self.goods = goods
        self.candidate_model = CandidateModel(self.tasks, self.blocks, self.trains, self.goods)

    def solve(self, horizon: PlanHorizon = PlanHorizon.WEEKLY) -> BlockPlan:
        """
        Executes fragmented department-by-department first-fit scheduling.
        """
        scheduled_tasks: List[ScheduledTask] = []
        unscheduled_tasks: List[str] = []
        
        # Track dynamic block state during greedy allocation
        block_slots_used: Dict[str, int] = {b.block_id: 0 for b in self.blocks}
        block_crew_used: Dict[str, int] = {b.block_id: 0 for b in self.blocks}
        block_map = {b.block_id: b for b in self.blocks}
        
        # Precedence tracker: map of task_id -> block_end_time
        completed_task_end_time: Dict[str, datetime] = {}

        # Siloed department execution order: Engineering -> S&T -> TRD
        dept_order = [Department.ENGINEERING, Department.S_AND_T, Department.TRD]

        for dept in dept_order:
            dept_tasks = [t for t in self.tasks if t.department == dept]
            # In current siloed practice, tasks are considered in arrival / order or priority
            dept_tasks.sort(key=lambda t: (-(t.priority_score or 0), t.earliest_start))

            for task in dept_tasks:
                assigned = False

                # Check precedence: have required predecessor tasks been scheduled?
                precedence_satisfied = True
                min_start_time = task.earliest_start
                for pred_id in task.precedence:
                    if pred_id not in completed_task_end_time:
                        precedence_satisfied = False
                        break
                    else:
                        min_start_time = max(min_start_time, completed_task_end_time[pred_id])

                if not precedence_satisfied:
                    unscheduled_tasks.append(task.task_id)
                    continue

                # First-fit search across sorted blocks
                for block in self.blocks:
                    # Feasibility check via CandidateModel
                    cand_eval = self.candidate_model.evaluate_pair(task, block)
                    if not cand_eval.feasible:
                        continue

                    # Precedence time check with this block
                    if block.start_time < min_start_time:
                        continue

                    # Capacity check
                    current_slots = block_slots_used[block.block_id]
                    current_crew = block_crew_used[block.block_id]

                    if (current_slots + 1 <= block.available_capacity and 
                        current_crew + task.crew_required <= block.resource_capacity):
                        # Assign to this block
                        block_slots_used[block.block_id] += 1
                        block_crew_used[block.block_id] += task.crew_required
                        
                        sch_task = ScheduledTask(
                            task_id=task.task_id,
                            block_id=block.block_id,
                            scheduled_start=block.start_time,
                            scheduled_end=block.start_time + (block.end_time - block.start_time),
                            status=TaskStatus.SCHEDULED,
                            explanation=f"Assigned by Baseline Greedy (First-Fit) to {block.block_id}",
                        )
                        scheduled_tasks.append(sch_task)
                        completed_task_end_time[task.task_id] = block.end_time
                        assigned = True
                        break

                if not assigned:
                    unscheduled_tasks.append(task.task_id)

        blocks_used = [b_id for b_id, count in block_slots_used.items() if count > 0]

        # Minimal temporary PlanMetrics (will be enriched via evaluator)
        dummy_metrics = PlanMetrics(
            total_tasks=len(self.tasks),
            scheduled_tasks_count=len(scheduled_tasks),
            unscheduled_tasks_count=len(unscheduled_tasks),
            total_critical_tasks=sum(1 for t in self.tasks if t.priority_band == "CRITICAL" or t.severity.value == "CRITICAL"),
            critical_tasks_completed=0,
            total_priority_score=sum(t.priority_score or 0.0 for t in self.tasks),
            completed_priority_score=0.0,
            priority_score_completion_pct=0.0,
            blocks_used_count=len(blocks_used),
            total_block_hours=sum(block_map[b_id].duration_hours for b_id in blocks_used),
            train_conflicts_count=0,
            total_train_disruption_penalty=0.0,
            goods_traffic_penalty=0.0,
            average_block_utilization_pct=0.0,
            multi_department_clubbed_blocks_count=0,
            simulated_asset_availability_pct=0.0,
        )

        return BlockPlan(
            plan_id=f"PLAN-BASELINE-{uuid.uuid4().hex[:6].upper()}",
            horizon=horizon,
            generated_at=datetime.now(),
            scheduled_tasks=scheduled_tasks,
            unscheduled_tasks=unscheduled_tasks,
            blocks_used=blocks_used,
            metrics=dummy_metrics,
            warnings=["Generated using siloed greedy baseline scheduler without cross-department optimization."],
            solver_status=SolverStatus.FEASIBLE,
        )

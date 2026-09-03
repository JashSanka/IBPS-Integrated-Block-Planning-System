"""
Block Opportunity / Candidate Generation Model.
Evaluates feasibility for every (task, block) pair across physical, temporal,
departmental, safety, and operational constraints.
Provides structured reasons for feasibility or rejection to explain decisions.
"""

from typing import List, Dict, Tuple
from datetime import datetime

from app.domain.models import (
    MaintenanceTask,
    BlockWindow,
    TrainMovement,
    GoodsForecast,
    CandidateEvaluation,
)
from app.domain.enums import Department, TrafficDensity


class CandidateModel:
    """Evaluates task-to-block feasibility and generates structured candidate pairings."""

    def __init__(
        self,
        tasks: List[MaintenanceTask],
        blocks: List[BlockWindow],
        trains: List[TrainMovement],
        goods: List[GoodsForecast],
    ):
        self.tasks = {t.task_id: t for t in tasks}
        self.blocks = {b.block_id: b for b in blocks}
        self.trains = trains
        self.goods = goods

    def has_hard_train_conflict(self, block: BlockWindow) -> Tuple[bool, List[str]]:
        """
        Detects if block overlaps with a Priority-1 train (Vande Bharat / Rajdhani)
        which forbids heavy possession unless rerouted.
        """
        conflicts = []
        for trn in self.trains:
            if trn.corridor_id == block.corridor_id:
                # Check time overlap
                if max(block.start_time, trn.start_time) < min(block.end_time, trn.end_time):
                    if trn.operational_priority == 1:
                        conflicts.append(
                            f"TRAIN_CONFLICT: Premium train {trn.train_id} ({trn.train_type.value}) operating {trn.start_time.strftime('%H:%M')}-{trn.end_time.strftime('%H:%M')}"
                        )
        return (len(conflicts) > 0, conflicts)

    def evaluate_pair(self, task: MaintenanceTask, block: BlockWindow) -> CandidateEvaluation:
        """Evaluates feasibility of assigning a specific task to a specific block."""
        reasons: List[str] = []
        is_feasible = True

        # 1. Corridor match
        if task.corridor_id != block.corridor_id:
            is_feasible = False
            reasons.append(f"CORRIDOR_MISMATCH: Task corridor '{task.corridor_id}' != Block corridor '{block.corridor_id}'")

        # 2. Department permission
        if task.department not in block.permitted_departments:
            is_feasible = False
            reasons.append(f"DEPARTMENT_NOT_PERMITTED: Department '{task.department.value}' not allowed in block '{block.block_id}'")

        # 3. Duration fit
        if task.estimated_duration_min > block.duration_minutes:
            is_feasible = False
            reasons.append(f"DURATION_EXCEEDED: Task requires {task.estimated_duration_min} min, block is {block.duration_minutes} min")

        # 4. Time bounds (Earliest start & Deadline)
        if block.start_time < task.earliest_start:
            is_feasible = False
            reasons.append(f"EARLY_START_VIOLATION: Block starts {block.start_time} before task earliest {task.earliest_start}")
        
        if block.end_time > task.deadline:
            is_feasible = False
            reasons.append(f"DEADLINE_EXCEEDED: Block ends {block.end_time} after task deadline {task.deadline}")

        # 5. Resource / Crew fit (individual task vs block capacity)
        if task.crew_required > block.resource_capacity:
            is_feasible = False
            reasons.append(f"INSUFFICIENT_CREW_CAPACITY: Task needs {task.crew_required} crew, block max is {block.resource_capacity}")

        # 6. Safety requirement check
        # TRD OHE work typically requires POWER_BLOCK_AVAILABLE
        if task.department == Department.TRD and "POWER_BLOCK_AVAILABLE" not in block.safety_constraints:
            is_feasible = False
            reasons.append("SAFETY_CONSTRAINT_MISSING: TRD task requires 'POWER_BLOCK_AVAILABLE'")

        # 7. Operational Train conflicts
        has_train_conflict, train_reasons = self.has_hard_train_conflict(block)
        if has_train_conflict:
            is_feasible = False
            reasons.extend(train_reasons)

        if is_feasible:
            reasons.append("FEASIBLE_CANDIDATE: All physical, temporal, safety and operational checks passed.")

        return CandidateEvaluation(
            task_id=task.task_id,
            block_id=block.block_id,
            feasible=is_feasible,
            reasons=reasons,
        )

    def evaluate_all(self) -> Dict[Tuple[str, str], CandidateEvaluation]:
        """Evaluates all (task, block) combinations."""
        candidates = {}
        for t_id, task in self.tasks.items():
            for b_id, block in self.blocks.items():
                candidates[(t_id, b_id)] = self.evaluate_pair(task, block)
        return candidates

    def get_feasible_blocks_for_task(self, task_id: str) -> List[str]:
        """Returns list of feasible block IDs for a given task."""
        task = self.tasks[task_id]
        feasible = []
        for b_id, block in self.blocks.items():
            eval_res = self.evaluate_pair(task, block)
            if eval_res.feasible:
                feasible.append(b_id)
        return feasible

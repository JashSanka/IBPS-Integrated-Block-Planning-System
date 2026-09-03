"""
Task Service - Querying, Filtering, and Explainable Candidate Feasibility for Tasks.
"""

from typing import List, Optional, Dict, Any
from app.domain.models import MaintenanceTask
from app.domain.enums import Department, PriorityBand, TaskStatus
from app.schemas.tasks import (
    TaskItemResponse,
    TaskDetailResponse,
    CandidateFeasibilityItem,
)
from app.optimization.candidate_model import CandidateModel
from app.services.state_service import get_state


class TaskService:
    @staticmethod
    def _to_item_response(task: MaintenanceTask, scheduled_map: Dict[str, Any]) -> TaskItemResponse:
        sch_info = scheduled_map.get(task.task_id)
        return TaskItemResponse(
            task_id=task.task_id,
            department=task.department,
            asset_id=task.asset_id,
            asset_type=task.asset_type,
            corridor_id=task.corridor_id,
            location=task.location,
            defect_type=task.defect_type,
            severity=task.severity,
            criticality=task.criticality,
            safety_risk=task.safety_risk,
            overdue_days=task.overdue_days,
            estimated_duration_min=task.estimated_duration_min,
            crew_required=task.crew_required,
            resource_requirements=task.resource_requirements,
            precedence=task.precedence,
            incompatible_tasks=task.incompatible_tasks,
            earliest_start=task.earliest_start,
            deadline=task.deadline,
            status=TaskStatus.SCHEDULED if sch_info else TaskStatus.UNSCHEDULED,
            traffic_criticality=task.traffic_criticality,
            priority_score=task.priority_score,
            priority_band=task.priority_band,
            score_breakdown=task.score_breakdown,
            scheduled_block_id=sch_info.block_id if sch_info else None,
            scheduled_start=sch_info.scheduled_start if sch_info else None,
            scheduled_end=sch_info.scheduled_end if sch_info else None,
            assignment_explanation=sch_info.explanation if sch_info else "Unscheduled in current plan cycle",
        )

    @staticmethod
    def get_tasks(
        department: Optional[Department] = None,
        corridor: Optional[str] = None,
        priority_band: Optional[PriorityBand] = None,
        status: Optional[TaskStatus] = None,
        search: Optional[str] = None,
    ) -> List[TaskItemResponse]:
        state = get_state()
        tasks = state.tasks
        opt_plan = state.optimized_plan
        scheduled_map = {st.task_id: st for st in (opt_plan.scheduled_tasks if opt_plan else [])}

        results = []
        for task in tasks:
            if department and task.department != department:
                continue
            if corridor and task.corridor_id.lower() != corridor.lower():
                continue
            if priority_band and task.priority_band != priority_band:
                continue
            is_sch = task.task_id in scheduled_map
            if status:
                if status == TaskStatus.SCHEDULED and not is_sch:
                    continue
                if status == TaskStatus.UNSCHEDULED and is_sch:
                    continue

            if search:
                s = search.lower()
                matches = (
                    s in task.task_id.lower()
                    or s in task.defect_type.lower()
                    or s in task.location.lower()
                    or s in task.asset_id.lower()
                    or s in task.asset_type.lower()
                    or s in task.corridor_id.lower()
                )
                if not matches:
                    continue

            results.append(TaskService._to_item_response(task, scheduled_map))

        # Sort by priority score descending
        results.sort(key=lambda t: -(t.priority_score or 0.0))
        return results

    @staticmethod
    def get_task_detail(task_id: str) -> Optional[TaskDetailResponse]:
        state = get_state()
        task = next((t for t in state.tasks if t.task_id == task_id), None)
        if not task:
            # Check emergency task
            if state.emergency_task and state.emergency_task.task_id == task_id:
                task = state.emergency_task
            else:
                return None

        opt_plan = state.optimized_plan
        scheduled_map = {st.task_id: st for st in (opt_plan.scheduled_tasks if opt_plan else [])}
        item = TaskService._to_item_response(task, scheduled_map)

        candidate_model = CandidateModel(state.tasks, state.blocks, state.trains, state.goods)
        cand_evals = []
        feasible_blocks = []

        for block in state.blocks:
            eval_res = candidate_model.evaluate_pair(task, block)
            if eval_res.feasible:
                feasible_blocks.append(block.block_id)
            cand_evals.append(CandidateFeasibilityItem(
                block_id=block.block_id,
                corridor_id=block.corridor_id,
                start_time=block.start_time,
                end_time=block.end_time,
                duration_minutes=block.duration_minutes,
                feasible=eval_res.feasible,
                reasons=eval_res.reasons,
            ))

        # Dependencies details
        precedence_details = []
        for pred_id in task.precedence:
            pred_task = next((t for t in state.tasks if t.task_id == pred_id), None)
            if pred_task:
                precedence_details.append({
                    "task_id": pred_task.task_id,
                    "department": pred_task.department.value,
                    "defect_type": pred_task.defect_type,
                    "priority_score": pred_task.priority_score,
                    "status": "SCHEDULED" if pred_task.task_id in scheduled_map else "UNSCHEDULED",
                })

        # Incompatibility details
        incomp_details = []
        for incomp_id in task.incompatible_tasks:
            incomp_task = next((t for t in state.tasks if t.task_id == incomp_id), None)
            if incomp_task:
                incomp_details.append({
                    "task_id": incomp_task.task_id,
                    "department": incomp_task.department.value,
                    "defect_type": incomp_task.defect_type,
                    "reason": "Exclusive physical/spatial/equipment hazard on same section.",
                })

        current_block_info = None
        if item.scheduled_block_id:
            blk = next((b for b in state.blocks if b.block_id == item.scheduled_block_id), None)
            if blk:
                current_block_info = {
                    "block_id": blk.block_id,
                    "corridor_id": blk.corridor_id,
                    "start_time": blk.start_time.isoformat(),
                    "end_time": blk.end_time.isoformat(),
                    "duration_hours": blk.duration_hours,
                    "traffic_density": blk.traffic_density.value,
                }

        return TaskDetailResponse(
            task=item,
            feasible_blocks_count=len(feasible_blocks),
            feasible_blocks=feasible_blocks,
            candidate_evaluations=cand_evals,
            precedence_tasks_details=precedence_details,
            incompatible_tasks_details=incomp_details,
            current_scheduled_block=current_block_info,
        )

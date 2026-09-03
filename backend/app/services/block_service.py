"""
Block Service - Querying and Detail Inspection for Corridor Block Windows.
"""

from typing import List, Optional, Dict, Any
from app.domain.models import BlockWindow
from app.domain.enums import Department
from app.schemas.blocks import (
    BlockItemResponse,
    BlockDetailResponse,
    BlockTaskAssignmentSummary,
    BlockTrainImpactSummary,
    BlockFreightImpactSummary,
)
from app.services.state_service import get_state


class BlockService:
    @staticmethod
    def get_blocks(corridor: Optional[str] = None) -> List[BlockItemResponse]:
        state = get_state()
        blocks = state.blocks
        tasks = {t.task_id: t for t in state.tasks}
        trains = state.trains
        opt_plan = state.optimized_plan
        scheduled_tasks = opt_plan.scheduled_tasks if opt_plan else []

        results = []
        for block in blocks:
            if corridor and block.corridor_id.lower() != corridor.lower():
                continue

            b_tasks = [st for st in scheduled_tasks if st.block_id == block.block_id]
            used_slots = len(b_tasks)
            used_crew = sum(tasks[st.task_id].crew_required for st in b_tasks if st.task_id in tasks)
            assigned_depts = sorted(list({tasks[st.task_id].department for st in b_tasks if st.task_id in tasks}))

            # Train disruption cost
            train_cost = 0.0
            for trn in trains:
                if trn.corridor_id == block.corridor_id:
                    if max(block.start_time, trn.start_time) < min(block.end_time, trn.end_time):
                        train_cost += trn.disruption_penalty

            slot_util = (used_slots / block.available_capacity * 100.0) if block.available_capacity > 0 else 0.0
            crew_util = (used_crew / block.resource_capacity * 100.0) if block.resource_capacity > 0 else 0.0

            results.append(BlockItemResponse(
                block_id=block.block_id,
                corridor_id=block.corridor_id,
                start_time=block.start_time,
                end_time=block.end_time,
                duration_minutes=block.duration_minutes,
                duration_hours=block.duration_hours,
                available_capacity=block.available_capacity,
                resource_capacity=block.resource_capacity,
                safety_constraints=block.safety_constraints,
                permitted_departments=block.permitted_departments,
                traffic_density=block.traffic_density,
                used_slots=used_slots,
                used_crew=used_crew,
                slot_utilization_pct=round(slot_util, 1),
                crew_utilization_pct=round(crew_util, 1),
                assigned_departments=assigned_depts,
                is_multi_department_clubbed=len(assigned_depts) >= 2,
                scheduled_tasks_count=len(b_tasks),
                train_disruption_cost=round(train_cost, 1),
            ))

        # Sort by start_time ascending
        results.sort(key=lambda b: b.start_time)
        return results

    @staticmethod
    def get_block_detail(block_id: str) -> Optional[BlockDetailResponse]:
        state = get_state()
        block = next((b for b in state.blocks if b.block_id == block_id), None)
        if not block:
            return None

        tasks = {t.task_id: t for t in state.tasks}
        if state.emergency_task:
            tasks[state.emergency_task.task_id] = state.emergency_task

        trains = state.trains
        goods = state.goods
        opt_plan = state.optimized_plan
        scheduled_tasks = opt_plan.scheduled_tasks if opt_plan else []

        b_tasks = [st for st in scheduled_tasks if st.block_id == block.block_id]
        used_slots = len(b_tasks)
        used_crew = sum(tasks[st.task_id].crew_required for st in b_tasks if st.task_id in tasks)
        assigned_depts = sorted(list({tasks[st.task_id].department for st in b_tasks if st.task_id in tasks}))

        train_cost = 0.0
        train_impacts = []
        for trn in trains:
            if trn.corridor_id == block.corridor_id:
                if max(block.start_time, trn.start_time) < min(block.end_time, trn.end_time):
                    train_cost += trn.disruption_penalty
                    train_impacts.append(BlockTrainImpactSummary(
                        train_id=trn.train_id,
                        train_type=trn.train_type,
                        direction=trn.direction,
                        start_time=trn.start_time,
                        end_time=trn.end_time,
                        operational_priority=trn.operational_priority,
                        disruption_penalty=trn.disruption_penalty,
                        is_hard_conflict=trn.operational_priority == 1,
                    ))

        freight_impacts = []
        for gf in goods:
            if gf.corridor_id == block.corridor_id:
                if max(block.start_time, gf.start_time) < min(block.end_time, gf.end_time):
                    freight_impacts.append(BlockFreightImpactSummary(
                        time_window=gf.time_window,
                        expected_goods_trains=gf.expected_goods_trains,
                        probability=gf.probability,
                        traffic_density=gf.traffic_density,
                    ))

        assigned_task_summaries = []
        for st in b_tasks:
            t = tasks.get(st.task_id)
            if t:
                assigned_task_summaries.append(BlockTaskAssignmentSummary(
                    task_id=t.task_id,
                    department=t.department,
                    defect_type=t.defect_type,
                    asset_id=t.asset_id,
                    priority_score=t.priority_score or 50.0,
                    priority_band=t.priority_band.value if t.priority_band else "ROUTINE",
                    crew_required=t.crew_required,
                    estimated_duration_min=t.estimated_duration_min,
                    scheduled_start=st.scheduled_start,
                    scheduled_end=st.scheduled_end,
                    explanation=st.explanation,
                ))

        slot_util = (used_slots / block.available_capacity * 100.0) if block.available_capacity > 0 else 0.0
        crew_util = (used_crew / block.resource_capacity * 100.0) if block.resource_capacity > 0 else 0.0

        item = BlockItemResponse(
            block_id=block.block_id,
            corridor_id=block.corridor_id,
            start_time=block.start_time,
            end_time=block.end_time,
            duration_minutes=block.duration_minutes,
            duration_hours=block.duration_hours,
            available_capacity=block.available_capacity,
            resource_capacity=block.resource_capacity,
            safety_constraints=block.safety_constraints,
            permitted_departments=block.permitted_departments,
            traffic_density=block.traffic_density,
            used_slots=used_slots,
            used_crew=used_crew,
            slot_utilization_pct=round(slot_util, 1),
            crew_utilization_pct=round(crew_util, 1),
            assigned_departments=assigned_depts,
            is_multi_department_clubbed=len(assigned_depts) >= 2,
            scheduled_tasks_count=len(b_tasks),
            train_disruption_cost=round(train_cost, 1),
        )

        if len(assigned_depts) >= 2:
            club_desc = f"Coordinated Multi-Department Block ({', '.join(d.value for d in assigned_depts)}) reducing total corridor closure."
        elif len(assigned_depts) == 1:
            club_desc = f"Single Department Block ({assigned_depts[0].value})."
        else:
            club_desc = "Unused / Open Block Window."

        safety_notes = [f"Safety Class / Granted: {', '.join(block.safety_constraints)}"]
        if "POWER_BLOCK_AVAILABLE" in block.safety_constraints:
            safety_notes.append("OHE 25kV de-energized and earthed — safe for TRD and bridge girder work.")
        if train_impacts:
            safety_notes.append(f"Caution: {len(train_impacts)} timetabled train movements recorded during window.")

        return BlockDetailResponse(
            block=item,
            assigned_tasks=assigned_task_summaries,
            train_conflicts=train_impacts,
            freight_forecasts=freight_impacts,
            clubbing_status_description=club_desc,
            safety_clearance_notes=safety_notes,
        )

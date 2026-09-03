"""
IBPS CP-SAT Constraint Optimization Engine.
Uses Google OR-Tools CP-SAT solver to compute globally optimal, conflict-free,
cross-department maintenance block schedules.
Includes solver audit/diagnostic reporting and what-if replanning diff generation.
"""

from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any, Set
import uuid

from ortools.sat.python import cp_model

from app.domain.models import (
    MaintenanceTask,
    BlockWindow,
    TrainMovement,
    GoodsForecast,
    ScheduledTask,
    BlockPlan,
    PlanMetrics,
    ReplanTaskChange,
    ReplanDiff,
    SolverDiagnosticReport,
)
from app.domain.enums import (
    Department,
    TaskStatus,
    SolverStatus,
    PlanHorizon,
    TrafficDensity,
)
from app.config import (
    AppConfig,
    OptimizationObjectiveWeights,
    SolverSettings,
    settings,
)
from app.optimization.candidate_model import CandidateModel
from app.scoring.priority_engine import PriorityEngine


class BlockPlanOptimizer:
    """CP-SAT Constraint Optimization Engine for Railway Maintenance Block Planning."""

    def __init__(
        self,
        tasks: List[MaintenanceTask],
        blocks: List[BlockWindow],
        trains: List[TrainMovement],
        goods: List[GoodsForecast],
        config: Optional[AppConfig] = None,
    ):
        self.config = config or settings
        self.priority_engine = PriorityEngine(
            weights=self.config.priority_weights,
            thresholds=self.config.priority_thresholds,
        )
        self.tasks = [t.model_copy(deep=True) for t in tasks]
        self.priority_engine.score_all(self.tasks)
        
        self.blocks = blocks
        self.trains = trains
        self.goods = goods
        
        self.task_map = {t.task_id: t for t in self.tasks}
        self.block_map = {b.block_id: b for b in self.blocks}
        self.candidate_model = CandidateModel(self.tasks, self.blocks, self.trains, self.goods)
        self.last_diagnostic_report: Optional[SolverDiagnosticReport] = None

    def _compute_block_train_disruption(self, block: BlockWindow) -> float:
        """Calculates total disruption penalty if block is activated."""
        penalty = 0.0
        for trn in self.trains:
            if trn.corridor_id == block.corridor_id:
                if max(block.start_time, trn.start_time) < min(block.end_time, trn.end_time):
                    penalty += trn.disruption_penalty
        return penalty

    def _compute_block_goods_traffic_cost(self, block: BlockWindow) -> int:
        """Calculates freight impact rating based on goods forecast."""
        cost = 0
        for gf in self.goods:
            if gf.corridor_id == block.corridor_id:
                if max(block.start_time, gf.start_time) < min(block.end_time, gf.end_time):
                    if gf.traffic_density == TrafficDensity.HIGH:
                        cost += 30
                    elif gf.traffic_density == TrafficDensity.MEDIUM:
                        cost += 15
                    else:
                        cost += 5
        return cost

    def solve(
        self,
        horizon: PlanHorizon = PlanHorizon.WEEKLY,
        enable_objective: bool = True,
        pinned_assignments: Optional[Dict[str, str]] = None,
    ) -> BlockPlan:
        """
        Builds and solves the CP-SAT model.
        - enable_objective: If False, solves purely as a Constraint Satisfaction Problem (CSP).
        - pinned_assignments: Optional task_id -> block_id map for what-if soft pinning.
        """
        model = cp_model.CpModel()
        obj_weights: OptimizationObjectiveWeights = self.config.objective_weights
        solver_settings: SolverSettings = self.config.solver_settings

        # -------------------------------------------------------------
        # 1. CANDIDATE FEASIBILITY & DECISION VARIABLES x[i, j]
        # -------------------------------------------------------------
        x: Dict[Tuple[str, str], cp_model.IntVar] = {}
        feasible_pairs: Set[Tuple[str, str]] = set()
        rejected_reasons_tally: Dict[str, int] = defaultdict(int)

        total_pairs = len(self.task_map) * len(self.block_map)
        for t_id, task in self.task_map.items():
            for b_id, block in self.block_map.items():
                eval_res = self.candidate_model.evaluate_pair(task, block)
                if eval_res.feasible:
                    x[(t_id, b_id)] = model.NewBoolVar(f"x_{t_id}_{b_id}")
                    feasible_pairs.add((t_id, b_id))
                else:
                    for reason in eval_res.reasons:
                        category = reason.split(":")[0] if ":" in reason else reason
                        rejected_reasons_tally[category] += 1

        # Auxiliary: is_scheduled[i] for each task
        is_scheduled: Dict[str, cp_model.IntVar] = {}
        for t_id in self.task_map:
            assigned_blocks = [x[(t_id, b_id)] for (t, b_id) in feasible_pairs if t == t_id]
            if assigned_blocks:
                is_sch_var = model.NewBoolVar(f"is_scheduled_{t_id}")
                model.Add(is_sch_var == sum(assigned_blocks))
                is_scheduled[t_id] = is_sch_var
            else:
                is_sch_var = model.NewBoolVar(f"is_scheduled_{t_id}")
                model.Add(is_sch_var == 0)
                is_scheduled[t_id] = is_sch_var

        # Auxiliary: block_used[j] for each block
        block_used: Dict[str, cp_model.IntVar] = {}
        for b_id, block in self.block_map.items():
            tasks_in_block = [x[(t_id, b_id)] for (t_id, b) in feasible_pairs if b == b_id]
            b_used_var = model.NewBoolVar(f"block_used_{b_id}")
            if tasks_in_block:
                for t_var in tasks_in_block:
                    model.Add(b_used_var >= t_var)
                model.Add(b_used_var <= sum(tasks_in_block))
            else:
                model.Add(b_used_var == 0)
            block_used[b_id] = b_used_var

        # -------------------------------------------------------------
        # 2. HARD CONSTRAINTS
        # -------------------------------------------------------------

        # Constraint 1: Each task assigned to AT MOST ONE block
        for t_id in self.task_map:
            assigned_vars = [x[(t_id, b_id)] for (t, b_id) in feasible_pairs if t == t_id]
            if assigned_vars:
                model.Add(sum(assigned_vars) <= 1)

        # Constraint 2: Resource / Crew capacity per block
        for b_id, block in self.block_map.items():
            crew_terms = [
                x[(t_id, b_id)] * self.task_map[t_id].crew_required
                for (t_id, b) in feasible_pairs if b == b_id
            ]
            if crew_terms:
                model.Add(sum(crew_terms) <= block.resource_capacity)

        # Constraint 3: Available task slots capacity per block
        for b_id, block in self.block_map.items():
            slot_terms = [x[(t_id, b_id)] for (t_id, b) in feasible_pairs if b == b_id]
            if slot_terms:
                model.Add(sum(slot_terms) <= block.available_capacity)

        # Constraint 4: Precedence Dependencies
        for t_id, task in self.task_map.items():
            for pred_id in task.precedence:
                if pred_id in self.task_map:
                    # a) Predecessor must be scheduled if task is scheduled
                    model.Add(is_scheduled[t_id] <= is_scheduled[pred_id])

                    # b) Temporal ordering
                    for (t_b, b_B_id) in feasible_pairs:
                        if t_b != t_id:
                            continue
                        block_B = self.block_map[b_B_id]
                        for (t_a, b_A_id) in feasible_pairs:
                            if t_a != pred_id:
                                continue
                            block_A = self.block_map[b_A_id]
                            # If block B starts before block A ends, they cannot be chosen together
                            if block_B.start_time < block_A.end_time:
                                model.Add(x[(t_id, b_B_id)] + x[(pred_id, b_A_id)] <= 1)

        # Constraint 5: Safety Incompatibility & Equipment Mutual Exclusions
        for t_id, task in self.task_map.items():
            for incomp_id in task.incompatible_tasks:
                if incomp_id in self.task_map:
                    for b_id in self.block_map:
                        if (t_id, b_id) in x and (incomp_id, b_id) in x:
                            model.Add(x[(t_id, b_id)] + x[(incomp_id, b_id)] <= 1)

        # -------------------------------------------------------------
        # 3. CLUBBING AUXILIARY VARIABLES
        # -------------------------------------------------------------
        extra_depts_list = []
        for b_id, block in self.block_map.items():
            dept_vars = []
            for dept in [Department.ENGINEERING, Department.S_AND_T, Department.TRD]:
                dept_tasks = [
                    x[(t_id, b_id)] for (t_id, b) in feasible_pairs 
                    if b == b_id and self.task_map[t_id].department == dept
                ]
                if dept_tasks:
                    d_act = model.NewBoolVar(f"dept_{dept.value}_{b_id}")
                    for dt in dept_tasks:
                        model.Add(d_act >= dt)
                    model.Add(d_act <= sum(dept_tasks))
                    dept_vars.append(d_act)
            
            if len(dept_vars) >= 2:
                num_depts_var = model.NewIntVar(0, 3, f"num_depts_{b_id}")
                model.Add(num_depts_var == sum(dept_vars))
                extra_dept_var = model.NewIntVar(0, 2, f"extra_depts_{b_id}")
                model.Add(extra_dept_var >= num_depts_var - 1)
                model.Add(extra_dept_var <= num_depts_var)
                model.Add(extra_dept_var <= 2 * block_used[b_id])
                extra_depts_list.append((b_id, extra_dept_var))

        # -------------------------------------------------------------
        # 4. SOFT OBJECTIVE FUNCTION
        # -------------------------------------------------------------
        objective_terms = []
        obj_breakdown: Dict[str, float] = {}

        if enable_objective:
            # Term A: Priority-weighted task completion (scaled integer)
            priority_terms = []
            for (t_id, b_id), var in x.items():
                task = self.task_map[t_id]
                score_int = int(round((task.priority_score or 50.0) * obj_weights.priority_completion_multiplier))
                priority_terms.append(var * score_int)
            if priority_terms:
                objective_terms.append(sum(priority_terms))

            # Term B: Bonus for completing CRITICAL tasks
            critical_bonus_terms = []
            for t_id, is_sch_var in is_scheduled.items():
                task = self.task_map[t_id]
                if task.priority_band == "CRITICAL" or task.severity.value == "CRITICAL":
                    critical_bonus_terms.append(is_sch_var * obj_weights.critical_completion_bonus)
            if critical_bonus_terms:
                objective_terms.append(sum(critical_bonus_terms))

            # Term C: Penalty for leaving CRITICAL tasks unscheduled
            crit_penalty_terms = []
            for t_id, is_sch_var in is_scheduled.items():
                task = self.task_map[t_id]
                if task.priority_band == "CRITICAL" or task.severity.value == "CRITICAL":
                    crit_penalty_terms.append((1 - is_sch_var) * obj_weights.unscheduled_critical_penalty)
            if crit_penalty_terms:
                objective_terms.append(-sum(crit_penalty_terms))

            # Term D: Cross-department clubbing bonus
            clubbing_terms = []
            for b_id, extra_var in extra_depts_list:
                clubbing_terms.append(extra_var * obj_weights.clubbing_bonus_per_extra_dept)
            if clubbing_terms:
                objective_terms.append(sum(clubbing_terms))

            # Term E: Penalty for total block hours used
            block_hour_penalty_terms = []
            for b_id, b_used_var in block_used.items():
                block = self.block_map[b_id]
                dur_hours_scaled = int(round(block.duration_hours * obj_weights.block_usage_penalty_per_hour))
                block_hour_penalty_terms.append(b_used_var * dur_hours_scaled)
            if block_hour_penalty_terms:
                objective_terms.append(-sum(block_hour_penalty_terms))

            # Term F: Penalty for train operational disruption
            train_penalty_terms = []
            for b_id, b_used_var in block_used.items():
                block = self.block_map[b_id]
                disruption = self._compute_block_train_disruption(block)
                if disruption > 0:
                    scaled_disp = int(round(disruption * obj_weights.train_disruption_penalty_multiplier / 10.0))
                    train_penalty_terms.append(b_used_var * scaled_disp)
            if train_penalty_terms:
                objective_terms.append(-sum(train_penalty_terms))

            # Term G: Penalty for goods traffic density
            goods_penalty_terms = []
            for b_id, b_used_var in block_used.items():
                block = self.block_map[b_id]
                cost = self._compute_block_goods_traffic_cost(block)
                if cost > 0:
                    scaled_goods = cost * obj_weights.goods_traffic_penalty_multiplier
                    goods_penalty_terms.append(b_used_var * scaled_goods)
            if goods_penalty_terms:
                objective_terms.append(-sum(goods_penalty_terms))

            # Term H: Soft pinning for what-if re-planning
            if pinned_assignments:
                pin_terms = []
                for t_id, b_id in pinned_assignments.items():
                    if (t_id, b_id) in x:
                        pin_terms.append(x[(t_id, b_id)] * 250)
                if pin_terms:
                    objective_terms.append(sum(pin_terms))

            model.Maximize(sum(objective_terms))

        # -------------------------------------------------------------
        # 5. SOLVE
        # -------------------------------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = solver_settings.time_limit_seconds
        solver.parameters.num_workers = solver_settings.num_search_workers
        solver.parameters.log_search_progress = solver_settings.log_search_progress
        solver.parameters.random_seed = solver_settings.random_seed

        status_code = solver.Solve(model)

        # Map CP-SAT solver status
        solver_status = SolverStatus.UNKNOWN
        if status_code == cp_model.OPTIMAL:
            solver_status = SolverStatus.OPTIMAL
        elif status_code == cp_model.FEASIBLE:
            solver_status = SolverStatus.FEASIBLE
        elif status_code == cp_model.INFEASIBLE:
            solver_status = SolverStatus.INFEASIBLE
        elif status_code == cp_model.MODEL_INVALID:
            solver_status = SolverStatus.MODEL_INVALID

        # -------------------------------------------------------------
        # 6. EXTRACT SOLUTION
        # -------------------------------------------------------------
        scheduled_tasks: List[ScheduledTask] = []
        unscheduled_tasks: List[str] = []
        blocks_used_set: Set[str] = set()

        if status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for (t_id, b_id), var in x.items():
                if solver.Value(var) == 1:
                    block = self.block_map[b_id]
                    task = self.task_map[t_id]
                    blocks_used_set.add(b_id)

                    scheduled_tasks.append(
                        ScheduledTask(
                            task_id=t_id,
                            block_id=b_id,
                            scheduled_start=block.start_time,
                            scheduled_end=block.start_time + (block.end_time - block.start_time),
                            status=TaskStatus.SCHEDULED,
                            explanation=(
                                f"Assigned to {b_id} on corridor {block.corridor_id} ({block.traffic_density.value} traffic). "
                                f"Task Priority: {task.priority_score:.1f} ({task.priority_band.value if task.priority_band else 'ROUTINE'}). "
                                f"Duration: {task.estimated_duration_min} min, Crew: {task.crew_required}."
                            ),
                        )
                    )

            scheduled_ids = {st.task_id for st in scheduled_tasks}
            for t_id in self.task_map:
                if t_id not in scheduled_ids:
                    unscheduled_tasks.append(t_id)

            if enable_objective:
                obj_breakdown["total_objective_value"] = float(solver.ObjectiveValue())
                obj_breakdown["wall_time_seconds"] = float(solver.WallTime())
                
                # Compute individual term contributions
                val_prio = sum(solver.Value(x[(t, b)]) * int(round((self.task_map[t].priority_score or 50.0) * obj_weights.priority_completion_multiplier)) for (t, b) in x)
                val_crit_bonus = sum(solver.Value(is_scheduled[t]) * obj_weights.critical_completion_bonus for t in is_scheduled if self.task_map[t].priority_band == "CRITICAL" or self.task_map[t].severity.value == "CRITICAL")
                val_crit_pen = sum((1 - solver.Value(is_scheduled[t])) * obj_weights.unscheduled_critical_penalty for t in is_scheduled if self.task_map[t].priority_band == "CRITICAL" or self.task_map[t].severity.value == "CRITICAL")
                val_club = sum(solver.Value(extra_var) * obj_weights.clubbing_bonus_per_extra_dept for b, extra_var in extra_depts_list)
                val_b_hour = sum(solver.Value(block_used[b]) * int(round(self.block_map[b].duration_hours * obj_weights.block_usage_penalty_per_hour)) for b in block_used)
                val_train = sum(solver.Value(block_used[b]) * int(round(self._compute_block_train_disruption(self.block_map[b]) * obj_weights.train_disruption_penalty_multiplier / 10.0)) for b in block_used)
                val_goods = sum(solver.Value(block_used[b]) * (self._compute_block_goods_traffic_cost(self.block_map[b]) * obj_weights.goods_traffic_penalty_multiplier) for b in block_used)

                obj_breakdown["priority_completion_term"] = float(val_prio)
                obj_breakdown["critical_bonus_term"] = float(val_crit_bonus)
                obj_breakdown["unscheduled_critical_penalty_term"] = float(-val_crit_pen)
                obj_breakdown["clubbing_bonus_term"] = float(val_club)
                obj_breakdown["block_hours_penalty_term"] = float(-val_b_hour)
                obj_breakdown["train_disruption_penalty_term"] = float(-val_train)
                obj_breakdown["goods_traffic_penalty_term"] = float(-val_goods)

        blocks_used = sorted(list(blocks_used_set))

        # Diagnostic Report Generation
        unscheduled_reasons = {}
        for u_id in unscheduled_tasks:
            feasible_blks = self.candidate_model.get_feasible_blocks_for_task(u_id)
            if not feasible_blks:
                unscheduled_reasons[u_id] = ["NO_FEASIBLE_BLOCKS_MEETING_PHYSICAL_OR_TRAIN_CONSTRAINTS"]
            else:
                unscheduled_reasons[u_id] = [f"COMPETED_OUT_BY_HIGHER_PRIORITY_TASKS (Feasible blocks: {', '.join(feasible_blks)})"]

        dept_combos = {}
        for b_id in blocks_used:
            b_tasks = [st for st in scheduled_tasks if st.block_id == b_id]
            depts = sorted(list({self.task_map[st.task_id].department.value for st in b_tasks}))
            dept_combos[b_id] = depts

        self.last_diagnostic_report = SolverDiagnosticReport(
            total_candidate_pairs=total_pairs,
            feasible_pairs_count=len(feasible_pairs),
            rejected_pairs_count=total_pairs - len(feasible_pairs),
            rejected_reasons_tally=dict(rejected_reasons_tally),
            scheduled_tasks_count=len(scheduled_tasks),
            unscheduled_tasks_count=len(unscheduled_tasks),
            unscheduled_tasks_details=unscheduled_reasons,
            blocks_used=blocks_used,
            department_combinations_by_block=dept_combos,
            objective_contributions=obj_breakdown,
            solver_wall_time_seconds=float(solver.WallTime()),
        )

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
            total_block_hours=sum(self.block_map[b_id].duration_hours for b_id in blocks_used),
            train_conflicts_count=0,
            total_train_disruption_penalty=0.0,
            goods_traffic_penalty=0.0,
            average_block_utilization_pct=0.0,
            multi_department_clubbed_blocks_count=0,
            simulated_asset_availability_pct=0.0,
        )

        return BlockPlan(
            plan_id=f"PLAN-OPT-{uuid.uuid4().hex[:6].upper()}",
            horizon=horizon,
            generated_at=datetime.now(),
            scheduled_tasks=scheduled_tasks,
            unscheduled_tasks=unscheduled_tasks,
            blocks_used=blocks_used,
            metrics=dummy_metrics,
            warnings=[],
            solver_status=solver_status,
            objective_breakdown=obj_breakdown,
        )

    def compute_replan_diff(
        self,
        previous_plan: BlockPlan,
        new_plan: BlockPlan,
        emergency_task_id: str,
    ) -> ReplanDiff:
        """
        Computes structured diff showing exact task movements, additions, and displacements.
        """
        prev_assignments: Dict[str, str] = {st.task_id: st.block_id for st in previous_plan.scheduled_tasks}
        new_assignments: Dict[str, str] = {st.task_id: st.block_id for st in new_plan.scheduled_tasks}

        tasks_added: List[ReplanTaskChange] = []
        tasks_moved: List[ReplanTaskChange] = []
        tasks_displaced: List[ReplanTaskChange] = []
        tasks_unchanged: List[str] = []

        all_task_ids = set(prev_assignments.keys()) | set(new_assignments.keys()) | {emergency_task_id}

        for t_id in all_task_ids:
            in_prev = t_id in prev_assignments
            in_new = t_id in new_assignments

            if in_new and not in_prev:
                # Newly added / scheduled
                task = self.task_map.get(t_id)
                reason = "Emergency high-priority defect injected and accommodated into schedule." if t_id == emergency_task_id else "Accommodated in re-planned optimization cycle."
                tasks_added.append(ReplanTaskChange(
                    task_id=t_id,
                    action="ADDED",
                    previous_block_id=None,
                    new_block_id=new_assignments[t_id],
                    reason=reason,
                ))
            elif in_prev and not in_new:
                # Displaced / unscheduled
                task = self.task_map.get(t_id)
                prio = task.priority_score if task else 0.0
                tasks_displaced.append(ReplanTaskChange(
                    task_id=t_id,
                    action="DISPLACED",
                    previous_block_id=prev_assignments[t_id],
                    new_block_id=None,
                    reason=f"Displaced from block {prev_assignments[t_id]} to yield capacity for higher-priority work (Priority: {prio:.1f}).",
                ))
            elif in_prev and in_new:
                if prev_assignments[t_id] == new_assignments[t_id]:
                    tasks_unchanged.append(t_id)
                else:
                    tasks_moved.append(ReplanTaskChange(
                        task_id=t_id,
                        action="MOVED",
                        previous_block_id=prev_assignments[t_id],
                        new_block_id=new_assignments[t_id],
                        reason=f"Shifted from block {prev_assignments[t_id]} to {new_assignments[t_id]} to resolve capacity bottleneck while preserving completion.",
                    ))

        return ReplanDiff(
            previous_plan_id=previous_plan.plan_id,
            new_plan_id=new_plan.plan_id,
            emergency_task_id=emergency_task_id,
            tasks_added=tasks_added,
            tasks_moved=tasks_moved,
            tasks_displaced=tasks_displaced,
            tasks_unchanged=tasks_unchanged,
            metric_deltas=[],
        )

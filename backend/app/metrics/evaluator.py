"""
Metrics Evaluator & Baseline Comparison Engine.
Calculates all KPIs strictly from live schedule output.
Includes transparent formula for 'Simulated Asset Availability'.
Fixes zero-baseline comparison semantics for mathematically accurate reporting.
"""

from typing import List, Dict, Set, Tuple
from app.domain.models import (
    MaintenanceTask,
    BlockWindow,
    TrainMovement,
    GoodsForecast,
    BlockPlan,
    PlanMetrics,
    MetricComparison,
)
from app.domain.enums import Department, PriorityBand, Severity, TrafficDensity


class MetricsEvaluator:
    """Computes comprehensive plan KPIs and comparative metrics between Baseline and IBPS."""

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

    def evaluate_plan(self, plan: BlockPlan) -> PlanMetrics:
        """Computes all PlanMetrics for a given BlockPlan."""
        scheduled_tasks = plan.scheduled_tasks
        scheduled_task_ids = {st.task_id for st in scheduled_tasks}
        unscheduled_task_ids = [t_id for t_id in self.tasks if t_id not in scheduled_task_ids]

        total_tasks_count = len(self.tasks)
        scheduled_count = len(scheduled_tasks)
        unscheduled_count = len(unscheduled_task_ids)

        # Priority & Critical Tasks
        critical_tasks = [
            t for t in self.tasks.values()
            if (t.priority_band == PriorityBand.CRITICAL or t.severity == Severity.CRITICAL or (t.priority_score and t.priority_score >= 80.0))
        ]
        total_critical_count = len(critical_tasks)
        critical_completed_count = sum(1 for t in critical_tasks if t.task_id in scheduled_task_ids)

        total_priority_score = sum((t.priority_score or 50.0) for t in self.tasks.values())
        completed_priority_score = sum(
            (self.tasks[st.task_id].priority_score or 50.0)
            for st in scheduled_tasks
            if st.task_id in self.tasks
        )
        priority_completion_pct = (
            (completed_priority_score / total_priority_score * 100.0)
            if total_priority_score > 0 else 0.0
        )

        # Blocks used & Block Hours
        blocks_used_ids = sorted(list({st.block_id for st in scheduled_tasks}))
        total_block_hours = sum(
            self.blocks[b_id].duration_hours for b_id in blocks_used_ids if b_id in self.blocks
        )

        # Operational Train Disruption on Used Blocks
        train_conflicts_count = 0
        total_train_disruption_penalty = 0.0
        for b_id in blocks_used_ids:
            if b_id not in self.blocks:
                continue
            block = self.blocks[b_id]
            for trn in self.trains:
                if trn.corridor_id == block.corridor_id:
                    if max(block.start_time, trn.start_time) < min(block.end_time, trn.end_time):
                        train_conflicts_count += 1
                        total_train_disruption_penalty += trn.disruption_penalty

        # Goods Traffic Disruption
        goods_penalty = 0.0
        for b_id in blocks_used_ids:
            if b_id not in self.blocks:
                continue
            block = self.blocks[b_id]
            for gf in self.goods:
                if gf.corridor_id == block.corridor_id:
                    if max(block.start_time, gf.start_time) < min(block.end_time, gf.end_time):
                        if gf.traffic_density == TrafficDensity.HIGH:
                            goods_penalty += 30.0
                        elif gf.traffic_density == TrafficDensity.MEDIUM:
                            goods_penalty += 15.0

        # Block Capacity Utilization & Clubbing
        block_dept_map: Dict[str, Set[Department]] = {b_id: set() for b_id in blocks_used_ids}
        block_slots_map: Dict[str, int] = {b_id: 0 for b_id in blocks_used_ids}
        
        for st in scheduled_tasks:
            if st.block_id in block_dept_map and st.task_id in self.tasks:
                task = self.tasks[st.task_id]
                block_dept_map[st.block_id].add(task.department)
                block_slots_map[st.block_id] += 1

        multi_dept_clubbed_count = sum(1 for b_id, depts in block_dept_map.items() if len(depts) >= 2)

        # Average Utilization (%) across used blocks
        utilization_percentages = []
        for b_id in blocks_used_ids:
            if b_id in self.blocks:
                cap = self.blocks[b_id].available_capacity
                slots = block_slots_map[b_id]
                utilization_percentages.append(min(100.0, (slots / cap) * 100.0))
        
        avg_utilization = (
            sum(utilization_percentages) / len(utilization_percentages)
            if utilization_percentages else 0.0
        )

        # Transparent Proxy Formula for 'Simulated Asset Availability'
        unscheduled_critical_count = total_critical_count - critical_completed_count
        crit_ratio = (critical_completed_count / total_critical_count) if total_critical_count > 0 else 1.0
        prio_ratio = (completed_priority_score / total_priority_score) if total_priority_score > 0 else 1.0

        simulated_avail = (
            80.0
            + (12.0 * crit_ratio)
            + (5.0 * prio_ratio)
            - (2.5 * unscheduled_critical_count)
            - (0.5 * train_conflicts_count)
        )
        simulated_avail = round(min(99.9, max(45.0, simulated_avail)), 2)

        metrics = PlanMetrics(
            total_tasks=total_tasks_count,
            scheduled_tasks_count=scheduled_count,
            unscheduled_tasks_count=unscheduled_count,
            total_critical_tasks=total_critical_count,
            critical_tasks_completed=critical_completed_count,
            total_priority_score=round(total_priority_score, 2),
            completed_priority_score=round(completed_priority_score, 2),
            priority_score_completion_pct=round(priority_completion_pct, 2),
            blocks_used_count=len(blocks_used_ids),
            total_block_hours=round(total_block_hours, 2),
            train_conflicts_count=train_conflicts_count,
            total_train_disruption_penalty=round(total_train_disruption_penalty, 2),
            goods_traffic_penalty=round(goods_penalty, 2),
            average_block_utilization_pct=round(avg_utilization, 2),
            multi_department_clubbed_blocks_count=multi_dept_clubbed_count,
            simulated_asset_availability_pct=simulated_avail,
        )

        plan.metrics = metrics
        plan.blocks_used = blocks_used_ids
        plan.unscheduled_tasks = unscheduled_task_ids
        return metrics

    def compare_plans(self, baseline: BlockPlan, optimized: BlockPlan) -> List[MetricComparison]:
        """Produces side-by-side metric comparison table between Baseline and Optimized plans."""
        bm = baseline.metrics
        om = optimized.metrics

        def make_comp(name: str, display: str, b_val: float, o_val: float, unit: str, higher_is_better: bool) -> MetricComparison:
            delta = o_val - b_val
            if b_val != 0:
                if higher_is_better:
                    pct = ((o_val - b_val) / abs(b_val)) * 100.0
                else:
                    pct = ((b_val - o_val) / abs(b_val)) * 100.0
            else:
                if o_val == 0:
                    pct = 0.0
                else:
                    pct = 100.0 if (o_val > 0 if higher_is_better else o_val < 0) else -100.0

            return MetricComparison(
                metric_name=name,
                display_name=display,
                baseline_value=round(b_val, 2),
                optimized_value=round(o_val, 2),
                delta=round(delta, 2),
                improvement_pct=round(pct, 2),
                unit=unit,
                higher_is_better=higher_is_better,
            )

        comparisons = [
            make_comp(
                "critical_tasks_completed",
                "Critical Safety Defects Cleared",
                float(bm.critical_tasks_completed),
                float(om.critical_tasks_completed),
                "tasks",
                True,
            ),
            make_comp(
                "priority_score_completion_pct",
                "Priority Score Fulfilled",
                bm.priority_score_completion_pct,
                om.priority_score_completion_pct,
                "%",
                True,
            ),
            make_comp(
                "total_block_hours",
                "Total Track Possession Hours Used",
                bm.total_block_hours,
                om.total_block_hours,
                "hrs",
                False,
            ),
            make_comp(
                "multi_department_clubbed_blocks_count",
                "Cross-Department Coordinated Blocks",
                float(bm.multi_department_clubbed_blocks_count),
                float(om.multi_department_clubbed_blocks_count),
                "blocks",
                True,
            ),
            make_comp(
                "average_block_utilization_pct",
                "Average Block Capacity Utilization",
                bm.average_block_utilization_pct,
                om.average_block_utilization_pct,
                "%",
                True,
            ),
            make_comp(
                "train_conflicts_count",
                "Train Conflicts / Disruptions",
                float(bm.train_conflicts_count),
                float(om.train_conflicts_count),
                "conflicts",
                False,
            ),
            make_comp(
                "simulated_asset_availability_pct",
                "Simulated Asset Availability",
                bm.simulated_asset_availability_pct,
                om.simulated_asset_availability_pct,
                "%",
                True,
            ),
        ]

        return comparisons

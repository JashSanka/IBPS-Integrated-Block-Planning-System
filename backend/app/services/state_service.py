"""
State Service - In-Memory Deterministic State Manager.
Maintains active dataset, current baseline & optimized plans, and adapters.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import threading

from app.domain.models import (
    MaintenanceTask,
    BlockWindow,
    TrainMovement,
    GoodsForecast,
    BlockPlan,
)
from app.domain.enums import PlanHorizon
from app.data.generator import get_demo_fixture_data, generate_full_synthetic_dataset
from app.scoring.priority_engine import PriorityEngine
from app.optimization.baseline import BaselineScheduler
from app.optimization.optimizer import BlockPlanOptimizer
from app.metrics.evaluator import MetricsEvaluator
from app.adapters.synthetic import (
    SyntheticTMSAdapter,
    SyntheticSMMSAdapter,
    SyntheticTDMSAdapter,
    SyntheticCOAAdapter,
)


class StateService:
    """Singleton in-memory state manager for IBPS prototype."""
    _instance: Optional["StateService"] = None
    _lock: threading.RLock = threading.RLock()

    def __init__(self):
        self.active_dataset_type: str = "demo_fixture"
        self.tasks: List[MaintenanceTask] = []
        self.blocks: List[BlockWindow] = []
        self.trains: List[TrainMovement] = []
        self.goods: List[GoodsForecast] = []
        self.emergency_task: Optional[MaintenanceTask] = None

        # Adapters
        self.tms_adapter = SyntheticTMSAdapter()
        self.smms_adapter = SyntheticSMMSAdapter()
        self.tdms_adapter = SyntheticTDMSAdapter()
        self.coa_adapter = SyntheticCOAAdapter()

        # Cached Plans & Evaluator
        self.baseline_plan: Optional[BlockPlan] = None
        self.optimized_plan: Optional[BlockPlan] = None
        self.evaluator: Optional[MetricsEvaluator] = None
        self.priority_engine = PriorityEngine()

        # Initialize with demo fixture
        self.load_dataset("demo_fixture")

    @classmethod
    def get_instance(cls) -> "StateService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load_dataset(self, dataset_type: str = "demo_fixture") -> None:
        """Loads and scores dataset, resetting plan caches."""
        with self._lock:
            self.active_dataset_type = dataset_type
            if dataset_type == "full_dataset":
                t, b, tr, g = generate_full_synthetic_dataset(seed=42)
                _, _, _, _, em = get_demo_fixture_data()
                self.tasks = t
                self.blocks = b
                self.trains = tr
                self.goods = g
                self.emergency_task = em
            else:
                t, b, tr, g, em = get_demo_fixture_data()
                self.tasks = t
                self.blocks = b
                self.trains = tr
                self.goods = g
                self.emergency_task = em

            # Score all tasks
            self.priority_engine.score_all(self.tasks)
            if self.emergency_task:
                self.priority_engine.score_task(self.emergency_task)

            # Update adapters
            self.tms_adapter.set_tasks(self.tasks)
            self.smms_adapter.set_tasks(self.tasks)
            self.tdms_adapter.set_tasks(self.tasks)
            self.coa_adapter.set_data(self.blocks, self.trains, self.goods)

            # Evaluator
            self.evaluator = MetricsEvaluator(self.tasks, self.blocks, self.trains, self.goods)

            # Pre-generate deterministic baseline & optimized plans
            self._generate_initial_plans()

    def _generate_initial_plans(self) -> None:
        """Computes baseline and optimized plans deterministically."""
        # 1. Baseline
        baseline_scheduler = BaselineScheduler(self.tasks, self.blocks, self.trains, self.goods)
        self.baseline_plan = baseline_scheduler.solve(horizon=PlanHorizon.WEEKLY)
        self.evaluator.evaluate_plan(self.baseline_plan)

        # 2. Optimized
        optimizer = BlockPlanOptimizer(self.tasks, self.blocks, self.trains, self.goods)
        self.optimized_plan = optimizer.solve(horizon=PlanHorizon.WEEKLY, enable_objective=True)
        self.evaluator.evaluate_plan(self.optimized_plan)


# Global singleton helper
def get_state() -> StateService:
    return StateService.get_instance()

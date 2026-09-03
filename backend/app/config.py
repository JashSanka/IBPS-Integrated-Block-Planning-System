"""
IBPS Configuration Module
Contains priority weights, solver parameters, scoring thresholds, and system constants.
"""

from pydantic import BaseModel, Field


class PriorityScoringWeights(BaseModel):
    """Weights for explainable priority scoring. Must sum to 1.0."""
    w_severity: float = Field(default=0.25, description="Weight for defect severity")
    w_criticality: float = Field(default=0.25, description="Weight for asset criticality")
    w_safety_risk: float = Field(default=0.25, description="Weight for safety risk level")
    w_overdue: float = Field(default=0.15, description="Weight for overdue days")
    w_traffic_criticality: float = Field(default=0.10, description="Weight for corridor traffic criticality")

    def validate_weights(self) -> bool:
        return abs((self.w_severity + self.w_criticality + self.w_safety_risk + 
                    self.w_overdue + self.w_traffic_criticality) - 1.0) < 1e-4


class PriorityThresholds(BaseModel):
    """Score thresholds for priority band classification [0, 100]."""
    critical: float = 80.0
    high: float = 60.0
    medium: float = 40.0
    routine: float = 0.0


class OptimizationObjectiveWeights(BaseModel):
    """Weights for soft objective terms in CP-SAT optimizer (scaled to integers in solver)."""
    priority_completion_multiplier: int = Field(default=10, description="Multiplier for task priority score")
    critical_completion_bonus: int = Field(default=500, description="Bonus for completing a CRITICAL priority task")
    clubbing_bonus_per_extra_dept: int = Field(default=350, description="Bonus per extra department sharing the same block window")
    block_usage_penalty_per_hour: int = Field(default=40, description="Penalty per hour of block closure activated")
    train_disruption_penalty_multiplier: int = Field(default=15, description="Penalty multiplier for train disruption")
    goods_traffic_penalty_multiplier: int = Field(default=10, description="Penalty multiplier for goods traffic disruption")
    unscheduled_critical_penalty: int = Field(default=800, description="Heavy penalty for leaving a CRITICAL task unscheduled")


class SolverSettings(BaseModel):
    """CP-SAT Solver settings."""
    time_limit_seconds: float = 30.0
    num_search_workers: int = 1
    log_search_progress: bool = False
    random_seed: int = 42


class AppConfig(BaseModel):
    priority_weights: PriorityScoringWeights = PriorityScoringWeights()
    priority_thresholds: PriorityThresholds = PriorityThresholds()
    objective_weights: OptimizationObjectiveWeights = OptimizationObjectiveWeights()
    solver_settings: SolverSettings = SolverSettings()


# Global default configuration instance
settings = AppConfig()

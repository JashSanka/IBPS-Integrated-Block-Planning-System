"""
Explainable Rule-Based Priority Engine for Maintenance Tasks.
Calculates deterministic multi-factor priority scores with exact contributor breakdowns.
NOTE: This is a transparent, explainable rule-based model, NOT machine learning.
"""

from typing import Dict, Any, Tuple
from app.domain.models import MaintenanceTask
from app.domain.enums import Severity, PriorityBand
from app.config import PriorityScoringWeights, PriorityThresholds, settings


SEVERITY_SCALE = {
    Severity.CRITICAL: 100.0,
    Severity.MAJOR: 75.0,
    Severity.MINOR: 45.0,
    Severity.ROUTINE: 20.0,
}


class PriorityEngine:
    """
    Computes explainable, weighted priority scores for maintenance tasks.
    Formula:
      Priority Score = w_sev * Severity + w_crit * Criticality + 
                       w_safe * SafetyRisk + w_overdue * OverdueScore + 
                       w_traf * TrafficCriticality
    """
    def __init__(
        self,
        weights: PriorityScoringWeights = settings.priority_weights,
        thresholds: PriorityThresholds = settings.priority_thresholds,
    ):
        self.weights = weights
        self.thresholds = thresholds

    def compute_overdue_score(self, overdue_days: int) -> float:
        """Normalized overdue score: 0 days -> 0, 8+ days -> 100."""
        return min(100.0, max(0.0, overdue_days * 12.5))

    def evaluate_task(self, task: MaintenanceTask) -> Tuple[float, PriorityBand, Dict[str, float]]:
        """
        Evaluate a single task and return (total_score, priority_band, contributor_breakdown).
        """
        sev_norm = SEVERITY_SCALE.get(task.severity, 20.0)
        crit_norm = min(100.0, max(0.0, task.criticality))
        safe_norm = min(100.0, max(0.0, task.safety_risk))
        overdue_norm = self.compute_overdue_score(task.overdue_days)
        traf_norm = min(100.0, max(0.0, task.traffic_criticality))

        c_sev = self.weights.w_severity * sev_norm
        c_crit = self.weights.w_criticality * crit_norm
        c_safe = self.weights.w_safety_risk * safe_norm
        c_overdue = self.weights.w_overdue * overdue_norm
        c_traf = self.weights.w_traffic_criticality * traf_norm

        total_score = c_sev + c_crit + c_safe + c_overdue + c_traf
        total_score = round(min(100.0, max(0.0, total_score)), 2)

        # Derive Priority Band
        if total_score >= self.thresholds.critical:
            band = PriorityBand.CRITICAL
        elif total_score >= self.thresholds.high:
            band = PriorityBand.HIGH
        elif total_score >= self.thresholds.medium:
            band = PriorityBand.MEDIUM
        else:
            band = PriorityBand.ROUTINE

        breakdown = {
            "severity": round(c_sev, 2),
            "criticality": round(c_crit, 2),
            "safety_risk": round(c_safe, 2),
            "overdue": round(c_overdue, 2),
            "traffic_criticality": round(c_traf, 2),
        }

        return total_score, band, breakdown

    def score_task(self, task: MaintenanceTask) -> MaintenanceTask:
        """Mutates/updates task with computed priority_score, priority_band, and score_breakdown."""
        score, band, breakdown = self.evaluate_task(task)
        task.priority_score = score
        task.priority_band = band
        task.score_breakdown = breakdown
        return task

    def score_all(self, tasks: list[MaintenanceTask]) -> list[MaintenanceTask]:
        """Score a collection of maintenance tasks."""
        for t in tasks:
            self.score_task(t)
        return tasks

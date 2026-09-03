"""
Unit tests for PriorityEngine.
Verifies exact deterministic weighted scores, contributor breakdowns, and priority bands.
"""

from datetime import datetime, timedelta
from app.domain.models import MaintenanceTask
from app.domain.enums import Department, Severity, PriorityBand
from app.scoring.priority_engine import PriorityEngine
from app.config import PriorityScoringWeights, PriorityThresholds


def test_priority_engine_calculation():
    engine = PriorityEngine()
    
    # Task with CRITICAL severity, 90 criticality, 90 safety risk, 8 overdue days (max score 100), 80 traffic crit
    task = MaintenanceTask(
        task_id="TEST-ENG-01",
        department=Department.ENGINEERING,
        asset_id="AST-01",
        asset_type="RAIL_TRACK",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="RAIL_FRACTURE",
        severity=Severity.CRITICAL,  # 100.0 * 0.25 = 25.0
        criticality=90.0,            # 90.0 * 0.25  = 22.5
        safety_risk=90.0,            # 90.0 * 0.25  = 22.5
        overdue_days=8,              # 100.0 * 0.15 = 15.0
        traffic_criticality=80.0,    # 80.0 * 0.10  = 8.0
        estimated_duration_min=120,
        crew_required=4,
        earliest_start=datetime.now(),
        deadline=datetime.now() + timedelta(days=2),
    )

    scored_task = engine.score_task(task)
    
    # Expected: 25.0 + 22.5 + 22.5 + 15.0 + 8.0 = 93.0
    assert scored_task.priority_score == 93.0
    assert scored_task.priority_band == PriorityBand.CRITICAL
    assert scored_task.score_breakdown is not None
    assert scored_task.score_breakdown["severity"] == 25.0
    assert scored_task.score_breakdown["criticality"] == 22.5
    assert scored_task.score_breakdown["safety_risk"] == 22.5
    assert scored_task.score_breakdown["overdue"] == 15.0
    assert scored_task.score_breakdown["traffic_criticality"] == 8.0


def test_priority_engine_routine_band():
    engine = PriorityEngine()
    
    task = MaintenanceTask(
        task_id="TEST-TRD-01",
        department=Department.TRD,
        asset_id="AST-02",
        asset_type="OHE_WIRE",
        corridor_id="CSTM-KYN",
        location="KM 10",
        defect_type="ROUTINE_INSPECTION",
        severity=Severity.ROUTINE,   # 20.0 * 0.25 = 5.0
        criticality=20.0,            # 20.0 * 0.25 = 5.0
        safety_risk=20.0,            # 20.0 * 0.25 = 5.0
        overdue_days=0,              # 0.0 * 0.15  = 0.0
        traffic_criticality=30.0,    # 30.0 * 0.10 = 3.0
        estimated_duration_min=60,
        crew_required=2,
        earliest_start=datetime.now(),
        deadline=datetime.now() + timedelta(days=2),
    )

    scored_task = engine.score_task(task)
    # Expected: 5.0 + 5.0 + 5.0 + 0.0 + 3.0 = 18.0
    assert scored_task.priority_score == 18.0
    assert scored_task.priority_band == PriorityBand.ROUTINE

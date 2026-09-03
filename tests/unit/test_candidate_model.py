"""
Unit tests for Candidate Opportunity Model.
Verifies accurate evaluation of feasibility and rejection reasons.
"""

from datetime import datetime, timedelta
from app.domain.models import MaintenanceTask, BlockWindow, TrainMovement, GoodsForecast
from app.domain.enums import Department, Severity, TrainType, Direction, TrafficDensity
from app.optimization.candidate_model import CandidateModel


def test_candidate_corridor_mismatch():
    base_t = datetime(2026, 9, 1, 0, 0)
    task = MaintenanceTask(
        task_id="T1",
        department=Department.ENGINEERING,
        asset_id="A1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="DEF1",
        severity=Severity.MAJOR,
        criticality=70.0,
        safety_risk=70.0,
        estimated_duration_min=60,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )
    block = BlockWindow(
        block_id="B1",
        corridor_id="CSTM-KYN",  # Different corridor
        start_time=base_t + timedelta(hours=1),
        end_time=base_t + timedelta(hours=4),
        permitted_departments=[Department.ENGINEERING],
    )
    
    cand_model = CandidateModel([task], [block], [], [])
    eval_res = cand_model.evaluate_pair(task, block)
    assert not eval_res.feasible
    assert any("CORRIDOR_MISMATCH" in r for r in eval_res.reasons)


def test_candidate_train_conflict_rejection():
    base_t = datetime(2026, 9, 1, 0, 0)
    task = MaintenanceTask(
        task_id="T1",
        department=Department.ENGINEERING,
        asset_id="A1",
        asset_type="RAIL",
        corridor_id="KYN-PUN",
        location="KM 100",
        defect_type="DEF1",
        severity=Severity.MAJOR,
        criticality=70.0,
        safety_risk=70.0,
        estimated_duration_min=60,
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
    )
    block = BlockWindow(
        block_id="B1",
        corridor_id="KYN-PUN",
        start_time=base_t + timedelta(hours=10),
        end_time=base_t + timedelta(hours=13),
        permitted_departments=[Department.ENGINEERING],
    )
    # Priority-1 Vande Bharat train overlapping block
    train = TrainMovement(
        train_id="TRN-VB-01",
        corridor_id="KYN-PUN",
        train_type=TrainType.VANDE_BHARAT,
        direction=Direction.DOWN,
        start_time=base_t + timedelta(hours=11),
        end_time=base_t + timedelta(hours=12),
        operational_priority=1,
        disruption_penalty=800.0,
    )

    cand_model = CandidateModel([task], [block], [train], [])
    eval_res = cand_model.evaluate_pair(task, block)
    assert not eval_res.feasible
    assert any("TRAIN_CONFLICT" in r for r in eval_res.reasons)

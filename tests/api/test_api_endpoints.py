"""
FastAPI Integration & Endpoint Unit Tests using TestClient.
Tests all REST endpoints, query filters, error handling, plan generation, what-if replanning, and determinism.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.state_service import StateService


@pytest.fixture(scope="module")
def client():
    # Ensure fresh demo fixture loaded in state
    state = StateService.get_instance()
    state.load_dataset("demo_fixture")
    return TestClient(app)


def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["system"] == "IBPS"
    assert data["data_mode"] == "synthetic"


def test_api_dashboard(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "SYNTHETIC" in data["data_badge"]
    assert data["tasks"]["total"] == 21
    assert data["tasks"]["critical"] == 4
    assert data["blocks"]["available"] == 7
    assert len(data["metrics_summary"]) >= 5
    assert "ENGINEERING" in data["departments"]
    assert "KYN-PUN" in data["corridors"]


def test_api_tasks_list_and_filters(client):
    # 1. Full list
    res_all = client.get("/api/tasks")
    assert res_all.status_code == 200
    tasks = res_all.json()
    assert len(tasks) == 21

    # 2. Filter by department
    res_eng = client.get("/api/tasks?department=ENGINEERING")
    assert res_eng.status_code == 200
    for t in res_eng.json():
        assert t["department"] == "ENGINEERING"

    # 3. Filter by priority band
    res_crit = client.get("/api/tasks?priority_band=CRITICAL")
    assert res_crit.status_code == 200
    assert len(res_crit.json()) == 4
    for t in res_crit.json():
        assert t["priority_band"] == "CRITICAL"

    # 4. Search keyword
    res_search = client.get("/api/tasks?search=FRACTURE")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1
    assert "FRACTURE" in res_search.json()[0]["defect_type"]


def test_api_task_detail_valid_and_invalid(client):
    # Valid task detail
    res_valid = client.get("/api/tasks/TASK-ENG-001")
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["task"]["task_id"] == "TASK-ENG-001"
    assert data["task"]["priority_band"] == "CRITICAL"
    assert data["feasible_blocks_count"] >= 1
    assert len(data["candidate_evaluations"]) == 7

    # Invalid task ID (404)
    res_invalid = client.get("/api/tasks/TASK-DOES-NOT-EXIST")
    assert res_invalid.status_code == 404
    err = res_invalid.json()
    assert err["error"]["status_code"] == 404
    assert "not found" in err["error"]["message"].lower()


def test_api_blocks_list_and_detail(client):
    # Blocks list
    res_blocks = client.get("/api/blocks")
    assert res_blocks.status_code == 200
    blocks = res_blocks.json()
    assert len(blocks) == 7

    # Filter by corridor
    res_kp = client.get("/api/blocks?corridor=KYN-PUN")
    assert res_kp.status_code == 200
    for b in res_kp.json():
        assert b["corridor_id"] == "KYN-PUN"

    # Block detail
    res_detail = client.get("/api/blocks/BLK-KP-NIGHT-01")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["block"]["block_id"] == "BLK-KP-NIGHT-01"
    assert len(detail["assigned_tasks"]) >= 2
    assert "Coordinated" in detail["clubbing_status_description"]

    # Invalid block ID (404)
    res_invalid = client.get("/api/blocks/BLK-UNKNOWN")
    assert res_invalid.status_code == 404


def test_api_plans_baseline_and_optimize(client):
    # Generate Baseline Plan
    res_base = client.post("/api/plans/baseline?horizon=WEEKLY")
    assert res_base.status_code == 200
    base_data = res_base.json()
    assert base_data["plan_type"] == "baseline"
    assert base_data["scheduled_tasks_count"] > 0

    # Generate Optimized Plan
    res_opt = client.post("/api/plans/optimize", json={"horizon": "WEEKLY", "objective_profile": "balanced"})
    assert res_opt.status_code == 200
    opt_data = res_opt.json()
    assert opt_data["plan_type"] == "optimized"
    assert opt_data["solver_status"] in ("OPTIMAL", "FEASIBLE")
    assert opt_data["objective_value"] is not None
    assert opt_data["objective_value"] > 0
    assert opt_data["scheduled_tasks_count"] >= base_data["scheduled_tasks_count"]

    # Latest plan query
    res_latest = client.get("/api/plans/latest?plan_type=optimized")
    assert res_latest.status_code == 200
    assert res_latest.json()["plan_id"] == opt_data["plan_id"]


def test_api_plan_comparison(client):
    response = client.get("/api/plans/comparison")
    assert response.status_code == 200
    data = response.json()
    assert "baseline_plan_id" in data
    assert "optimized_plan_id" in data
    assert len(data["comparisons"]) >= 5
    for comp in data["comparisons"]:
        assert "metric_name" in comp
        assert "label" in comp
        assert isinstance(comp["delta"], (int, float))


def test_api_plans_diagnostics(client):
    response = client.get("/api/plans/diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_candidate_pairs"] == 147
    assert data["feasible_pairs_count"] > 0
    assert data["rejected_pairs_count"] > 0
    assert "CORRIDOR_MISMATCH" in data["rejected_reasons_tally"]
    assert "priority_completion_term" in data["objective_contributions"]


def test_api_what_if_emergency_replanning(client):
    payload = {
        "task": {
            "task_id": "EMERGENCY-ENG-999",
            "department": "ENGINEERING",
            "asset_id": "TRK-KP-118",
            "asset_type": "RAIL_TRACK",
            "corridor_id": "KYN-PUN",
            "location": "KM 118/6",
            "defect_type": "SUDDEN_TRANSVERSE_RAIL_CRACK",
            "severity": "CRITICAL",
            "criticality": 100.0,
            "safety_risk": 100.0,
            "duration_minutes": 120,
            "crew_required": 4,
            "traffic_criticality": 95.0,
        }
    }

    response = client.post("/api/plans/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "replanned"
    assert data["diff"]["emergency_task_id"] == "EMERGENCY-ENG-999"
    assert any(t["task_id"] == "EMERGENCY-ENG-999" for t in data["diff"]["tasks_added"])
    assert len(data["diff"]["tasks_displaced"]) >= 1
    assert len(data["diff"]["tasks_unchanged"]) >= 15


def test_api_what_if_invalid_payload(client):
    # Missing required task dictionary
    response = client.post("/api/plans/what-if", json={})
    assert response.status_code == 422


def test_api_deterministic_optimization_runs(client):
    # Consecutive calls to optimize with the same payload must produce the identical objective value
    res1 = client.post("/api/plans/optimize", json={"horizon": "WEEKLY", "objective_profile": "balanced"})
    res2 = client.post("/api/plans/optimize", json={"horizon": "WEEKLY", "objective_profile": "balanced"})
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json()["objective_value"] == res2.json()["objective_value"]
    assert res1.json()["scheduled_tasks_count"] == res2.json()["scheduled_tasks_count"]


def test_api_dataset_switching(client):
    # 1. Switch to full dataset
    res_switch = client.post("/api/datasets/switch", json={"dataset_type": "full_dataset"})
    assert res_switch.status_code == 200
    data = res_switch.json()
    assert data["active_dataset"] == "full_dataset"
    assert data["task_count"] == 200
    assert data["corridor_count"] == 12

    # 2. Check tasks list on full dataset
    res_tasks = client.get("/api/tasks")
    assert res_tasks.status_code == 200
    assert len(res_tasks.json()) == 200

    # 3. Switch back to demo fixture
    res_demo = client.post("/api/datasets/switch", json={"dataset_type": "demo_fixture"})
    assert res_demo.status_code == 200
    assert res_demo.json()["active_dataset"] == "demo_fixture"
    assert res_demo.json()["task_count"] == 21

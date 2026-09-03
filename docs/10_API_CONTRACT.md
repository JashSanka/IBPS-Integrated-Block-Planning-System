# IBPS API CONTRACT — Frontend & Integration Guide

**System:** IBPS (Integrated Block Planning System)  
**Version:** `1.0.0`  
**Base URL:** `http://127.0.0.1:8000/api`  
**Data Mode Notice:** `SYNTHETIC / DEMO DATA ONLY — ARCHITECTURAL PROTOTYPE`  
**Human-in-the-Loop Positioning:** *"IBPS provides AI-assisted decision support for maintenance block planning. Final approval and override remain with authorized railway personnel."*

---

## 1. System & Overview Endpoints

### 1.1 Health Check
- **Method:** `GET`
- **Path:** `/api/health`
- **Purpose:** Verifies backend service health, API version, and synthetic data mode.
- **Request:** None
- **Response (`200 OK`):**
```json
{
  "status": "ok",
  "system": "IBPS",
  "version": "1.0.0",
  "data_mode": "synthetic",
  "description": "AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways",
  "human_in_the_loop_notice": "IBPS provides AI-assisted decision support for maintenance block planning. Final approval and override remain with authorized railway personnel."
}
```

---

### 1.2 Dashboard Summary
- **Method:** `GET`
- **Path:** `/api/dashboard`
- **Purpose:** Returns high-level task metrics, corridor block window statistics, and side-by-side KPI deltas for the overview screen.
- **Request:** None
- **Response (`200 OK`):**
```json
{
  "data_badge": "SYNTHETIC / DEMO DATA ONLY — ARCHITECTURAL PROTOTYPE",
  "positioning_statement": "IBPS provides AI-assisted decision support for maintenance block planning. Final approval and override remain with authorized railway personnel.",
  "active_dataset": "demo_fixture",
  "tasks": {
    "total": 21,
    "critical": 4,
    "high": 10,
    "medium": 4,
    "routine": 3,
    "scheduled_baseline": 15,
    "scheduled_optimized": 18,
    "unscheduled_optimized": 3
  },
  "blocks": {
    "available": 7,
    "used_baseline": 6,
    "used_optimized": 6,
    "total_possession_hours_baseline": 18.0,
    "total_possession_hours_optimized": 18.0
  },
  "metrics_summary": [
    {
      "metric_name": "critical_tasks_completed",
      "display_name": "Critical Safety Defects Cleared",
      "baseline_value": 4.0,
      "optimized_value": 4.0,
      "delta": 0.0,
      "percentage_change": 0.0,
      "unit": "tasks",
      "higher_is_better": true,
      "label": "No change"
    },
    {
      "metric_name": "priority_score_completion_pct",
      "display_name": "Priority Score Fulfilled",
      "baseline_value": 76.6,
      "optimized_value": 94.1,
      "delta": 17.5,
      "percentage_change": 22.9,
      "unit": "%",
      "higher_is_better": true,
      "label": "+22.9%"
    },
    {
      "metric_name": "cross_department_clubbed_blocks",
      "display_name": "Cross-Department Coordinated Blocks",
      "baseline_value": 3.0,
      "optimized_value": 5.0,
      "delta": 2.0,
      "percentage_change": 66.7,
      "unit": "blocks",
      "higher_is_better": true,
      "label": "+66.7%"
    },
    {
      "metric_name": "simulated_asset_availability_pct",
      "display_name": "Simulated Asset Availability",
      "baseline_value": 95.3,
      "optimized_value": 96.2,
      "delta": 0.9,
      "percentage_change": 0.9,
      "unit": "%",
      "higher_is_better": true,
      "label": "+0.9%"
    }
  ],
  "departments": ["ENGINEERING", "S&T", "TRD"],
  "corridors": ["CSTM-KYN", "KYN-PUN", "NDLS-GZB"],
  "last_plan_generated_at": "2026-08-27T01:10:00"
}
```

---

## 2. Maintenance Tasks Endpoints

### 2.1 List Maintenance Tasks
- **Method:** `GET`
- **Path:** `/api/tasks`
- **Query Parameters:**
  - `department` (optional): `ENGINEERING`, `S&T`, `TRD`
  - `corridor` (optional): e.g. `KYN-PUN`
  - `priority_band` (optional): `CRITICAL`, `HIGH`, `MEDIUM`, `ROUTINE`
  - `status` (optional): `SCHEDULED`, `UNSCHEDULED`
  - `search` (optional): search string in defect, asset ID, or location
- **Response (`200 OK`):** List of `TaskItemResponse` objects.
```json
[
  {
    "task_id": "TASK-ENG-001",
    "department": "ENGINEERING",
    "asset_id": "TRK-KP-102",
    "asset_type": "RAIL_TRACK",
    "corridor_id": "KYN-PUN",
    "location": "KM 102/4-102/8",
    "defect_type": "SEVERE_RAIL_FRACTURE",
    "severity": "CRITICAL",
    "criticality": 96.0,
    "safety_risk": 98.0,
    "overdue_days": 14,
    "estimated_duration_min": 150,
    "crew_required": 4,
    "resource_requirements": ["WELDING_PLANT", "RAIL_CUTTER"],
    "precedence": [],
    "incompatible_tasks": [],
    "earliest_start": "2026-09-01T00:00:00",
    "deadline": "2026-09-03T00:00:00",
    "status": "SCHEDULED",
    "traffic_criticality": 90.0,
    "priority_score": 97.5,
    "priority_band": "CRITICAL",
    "score_breakdown": {
      "severity": 25.0,
      "criticality": 24.0,
      "safety_risk": 24.5,
      "overdue": 15.0,
      "traffic_criticality": 9.0
    },
    "scheduled_block_id": "BLK-KP-NIGHT-02",
    "scheduled_start": "2026-09-02T01:30:00",
    "scheduled_end": "2026-09-02T05:00:00",
    "assignment_explanation": "Assigned to BLK-KP-NIGHT-02 on corridor KYN-PUN (LOW traffic). Task Priority: 97.5 (CRITICAL)."
  }
]
```

---

### 2.2 Task Detail & Explainability
- **Method:** `GET`
- **Path:** `/api/tasks/{task_id}`
- **Purpose:** Full explainability showing why a task was prioritized, which candidate block windows were feasible, and why others were rejected.
- **Response (`200 OK`):**
```json
{
  "task": { ... },
  "feasible_blocks_count": 2,
  "feasible_blocks": ["BLK-KP-NIGHT-01", "BLK-KP-NIGHT-02"],
  "candidate_evaluations": [
    {
      "block_id": "BLK-KP-NIGHT-01",
      "corridor_id": "KYN-PUN",
      "start_time": "2026-09-01T01:30:00",
      "end_time": "2026-09-01T05:00:00",
      "duration_minutes": 210,
      "feasible": true,
      "reasons": ["FEASIBLE_CANDIDATE: All physical, temporal, safety and operational checks passed."]
    },
    {
      "block_id": "BLK-KP-DAY-PEAK",
      "corridor_id": "KYN-PUN",
      "start_time": "2026-09-01T11:00:00",
      "end_time": "2026-09-01T13:30:00",
      "duration_minutes": 150,
      "feasible": false,
      "reasons": ["TRAIN_CONFLICT: Premium train TRN-VB-22225 (VANDE_BHARAT) operating 11:30-12:15"]
    }
  ],
  "precedence_tasks_details": [],
  "incompatible_tasks_details": [],
  "current_scheduled_block": {
    "block_id": "BLK-KP-NIGHT-02",
    "corridor_id": "KYN-PUN",
    "start_time": "2026-09-02T01:30:00",
    "end_time": "2026-09-02T05:00:00",
    "duration_hours": 3.5,
    "traffic_density": "LOW"
  }
}
```
- **Error Response (`404 Not Found`):**
```json
{
  "error": {
    "status_code": 404,
    "message": "Maintenance task 'TASK-INVALID' was not found in active dataset.",
    "path": "/api/tasks/TASK-INVALID"
  }
}
```

---

## 3. Corridor Block Windows Endpoints

### 3.1 List Block Windows
- **Method:** `GET`
- **Path:** `/api/blocks`
- **Query Parameters:**
  - `corridor` (optional): filter by corridor section ID
- **Response (`200 OK`):**
```json
[
  {
    "block_id": "BLK-KP-NIGHT-01",
    "corridor_id": "KYN-PUN",
    "start_time": "2026-09-01T01:30:00",
    "end_time": "2026-09-01T05:00:00",
    "duration_minutes": 210,
    "duration_hours": 3.5,
    "available_capacity": 4,
    "resource_capacity": 12,
    "safety_constraints": ["POWER_BLOCK_AVAILABLE", "TRAFFIC_BLOCK_GRANTED"],
    "permitted_departments": ["ENGINEERING", "S&T", "TRD"],
    "traffic_density": "LOW",
    "used_slots": 4,
    "used_crew": 12,
    "slot_utilization_pct": 100.0,
    "crew_utilization_pct": 100.0,
    "assigned_departments": ["ENGINEERING", "S&T", "TRD"],
    "is_multi_department_clubbed": true,
    "scheduled_tasks_count": 4,
    "train_disruption_cost": 0.0
  }
]
```

---

### 3.2 Block Window Detail
- **Method:** `GET`
- **Path:** `/api/blocks/{block_id}`
- **Response (`200 OK`):**
```json
{
  "block": { ... },
  "assigned_tasks": [
    {
      "task_id": "TASK-TRD-001",
      "department": "TRD",
      "defect_type": "CANTILEVER_STAGGER_ADJUSTMENT",
      "asset_id": "OHE-KP-304",
      "priority_score": 63.9,
      "priority_band": "HIGH",
      "crew_required": 3,
      "estimated_duration_min": 110,
      "scheduled_start": "2026-09-01T01:30:00",
      "scheduled_end": "2026-09-01T05:00:00",
      "explanation": "Assigned to BLK-KP-NIGHT-01 on corridor KYN-PUN."
    }
  ],
  "train_conflicts": [],
  "freight_forecasts": [
    {
      "time_window": "NIGHT_00_06",
      "expected_goods_trains": 1,
      "probability": 0.4,
      "traffic_density": "LOW"
    }
  ],
  "clubbing_status_description": "Coordinated Multi-Department Block (ENGINEERING, S&T, TRD) reducing total corridor closure.",
  "safety_clearance_notes": [
    "Safety Class / Granted: POWER_BLOCK_AVAILABLE, TRAFFIC_BLOCK_GRANTED",
    "OHE 25kV de-energized and earthed — safe for TRD and bridge girder work."
  ]
}
```

---

## 4. Planning & Optimization Endpoints

### 4.1 Generate Fragmented Baseline Plan
- **Method:** `POST`
- **Path:** `/api/plans/baseline`
- **Query Parameter:** `horizon` (default `WEEKLY`)
- **Response (`200 OK`):** `PlanResponse` with `plan_type: "baseline"`.

---

### 4.2 Generate CP-SAT Optimized Plan
- **Method:** `POST`
- **Path:** `/api/plans/optimize`
- **Request Body:**
```json
{
  "horizon": "WEEKLY",
  "objective_profile": "balanced"
}
```
*(Options for `objective_profile`: `"balanced"`, `"high_safety"`, `"high_traffic_penalty"`, `"pure_csp"`)*
- **Response (`200 OK`):**
```json
{
  "plan_id": "PLAN-OPT-9A3F10",
  "plan_type": "optimized",
  "horizon": "WEEKLY",
  "generated_at": "2026-08-27T01:10:00",
  "solver_status": "OPTIMAL",
  "objective_value": 16378.0,
  "blocks_used": ["BLK-CK-NIGHT-01", "BLK-CK-NIGHT-02", "BLK-KP-ENG-EARLY", "BLK-KP-NIGHT-01", "BLK-KP-NIGHT-02", "BLK-NG-NIGHT-01"],
  "scheduled_tasks_count": 18,
  "unscheduled_tasks_count": 3,
  "scheduled_tasks": [ ... ],
  "unscheduled_tasks": ["TASK-ENG-003B", "TASK-TRD-004", "TASK-TRD-005"],
  "metrics": { ... },
  "objective_breakdown": {
    "total_objective_value": 16378.0,
    "priority_completion_term": 12098.0,
    "critical_bonus_term": 2000.0,
    "unscheduled_critical_penalty_term": 0.0,
    "clubbing_bonus_term": 3500.0,
    "block_hours_penalty_term": -720.0,
    "train_disruption_penalty_term": -300.0,
    "goods_traffic_penalty_term": -200.0
  }
}
```

---

### 4.3 Plan Comparison (Baseline vs. IBPS)
- **Method:** `GET`
- **Path:** `/api/plans/comparison`
- **Response (`200 OK`):**
```json
{
  "baseline_plan_id": "PLAN-BASELINE-5C28",
  "optimized_plan_id": "PLAN-OPT-9A3F10",
  "baseline_metrics": { ... },
  "optimized_metrics": { ... },
  "comparisons": [
    {
      "metric_name": "critical_tasks_completed",
      "display_name": "Critical Safety Defects Cleared",
      "baseline_value": 4.0,
      "optimized_value": 4.0,
      "delta": 0.0,
      "percentage_change": 0.0,
      "unit": "tasks",
      "higher_is_better": true,
      "label": "No change"
    },
    {
      "metric_name": "priority_score_completion_pct",
      "display_name": "Priority Score Fulfilled",
      "baseline_value": 76.6,
      "optimized_value": 94.1,
      "delta": 17.5,
      "percentage_change": 22.9,
      "unit": "%",
      "higher_is_better": true,
      "label": "+22.9%"
    },
    {
      "metric_name": "cross_department_clubbed_blocks",
      "display_name": "Cross-Department Coordinated Blocks",
      "baseline_value": 3.0,
      "optimized_value": 5.0,
      "delta": 2.0,
      "percentage_change": 66.7,
      "unit": "blocks",
      "higher_is_better": true,
      "label": "+66.7%"
    },
    {
      "metric_name": "average_block_utilization_pct",
      "display_name": "Average Block Capacity Utilization",
      "baseline_value": 76.4,
      "optimized_value": 94.4,
      "delta": 18.0,
      "percentage_change": 23.6,
      "unit": "%",
      "higher_is_better": true,
      "label": "+23.6%"
    },
    {
      "metric_name": "simulated_asset_availability_pct",
      "display_name": "Simulated Asset Availability",
      "baseline_value": 95.3,
      "optimized_value": 96.2,
      "delta": 0.9,
      "percentage_change": 0.9,
      "unit": "%",
      "higher_is_better": true,
      "label": "+0.9%"
    }
  ],
  "human_in_the_loop_positioning": "IBPS provides AI-assisted decision support for maintenance block planning. Final approval and override remain with authorized railway personnel."
}
```

---

## 5. What-If Scenario Re-planning

### 5.1 Inject Emergency Defect & Re-plan
- **Method:** `POST`
- **Path:** `/api/plans/what-if`
- **Request Body:**
```json
{
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
    "incompatible_tasks": []
  }
}
```
- **Response (`200 OK`):**
```json
{
  "status": "replanned",
  "before": { ... },
  "after": { ... },
  "diff": {
    "previous_plan_id": "PLAN-OPT-9A3F10",
    "new_plan_id": "PLAN-OPT-88DE41",
    "emergency_task_id": "EMERGENCY-ENG-999",
    "tasks_added": [
      {
        "task_id": "EMERGENCY-ENG-999",
        "action": "ADDED",
        "previous_block_id": null,
        "new_block_id": "BLK-KP-NIGHT-01",
        "reason": "Emergency high-priority defect injected and accommodated into schedule."
      }
    ],
    "tasks_moved": [],
    "tasks_displaced": [
      {
        "task_id": "TASK-ENG-HEAVY-009",
        "action": "DISPLACED",
        "previous_block_id": "BLK-KP-NIGHT-01",
        "new_block_id": null,
        "reason": "Displaced from block BLK-KP-NIGHT-01 to yield capacity for higher-priority work (Priority: 65.0)."
      }
    ],
    "tasks_unchanged": [
      "TASK-ENG-001",
      "TASK-ENG-002",
      "TASK-ENG-003A",
      "TASK-ENG-004",
      "TASK-ENG-005",
      "TASK-ENG-007",
      "TASK-ENG-008",
      "TASK-SNT-001",
      "TASK-SNT-002",
      "TASK-SNT-003",
      "TASK-SNT-004",
      "TASK-SNT-005",
      "TASK-TRD-001",
      "TASK-TRD-002",
      "TASK-TRD-003",
      "TASK-TRD-006",
      "TASK-TRD-INCOMP-009"
    ],
    "metric_deltas": [ ... ]
  },
  "kpi_impact": [ ... ]
}
```

---

## 6. Diagnostics & Datasets

### 6.1 Solver Diagnostic Report
- **Method:** `GET`
- **Path:** `/api/plans/diagnostics`
- **Response (`200 OK`):**
```json
{
  "total_candidate_pairs": 147,
  "feasible_pairs_count": 42,
  "rejected_pairs_count": 105,
  "rejected_reasons_tally": {
    "CORRIDOR_MISMATCH": 87,
    "TRAIN_CONFLICT": 21,
    "DEPARTMENT_NOT_PERMITTED": 17,
    "SAFETY_CONSTRAINT_MISSING": 12,
    "DURATION_EXCEEDED": 2
  },
  "objective_contributions": {
    "total_objective_value": 16378.0,
    "priority_completion_term": 12098.0,
    "critical_bonus_term": 2000.0,
    "unscheduled_critical_penalty_term": 0.0,
    "clubbing_bonus_term": 3500.0,
    "block_hours_penalty_term": -720.0,
    "train_disruption_penalty_term": -300.0,
    "goods_traffic_penalty_term": -200.0
  },
  "blocks_used_count": 6,
  "department_combinations_by_block": {
    "BLK-CK-NIGHT-01": ["ENGINEERING", "S&T", "TRD"],
    "BLK-CK-NIGHT-02": ["ENGINEERING", "S&T"],
    "BLK-KP-ENG-EARLY": ["ENGINEERING"],
    "BLK-KP-NIGHT-01": ["ENGINEERING", "S&T", "TRD"],
    "BLK-KP-NIGHT-02": ["ENGINEERING", "S&T", "TRD"],
    "BLK-NG-NIGHT-01": ["ENGINEERING", "S&T"]
  },
  "unscheduled_tasks_diagnostics": {
    "TASK-ENG-003B": ["COMPETED_OUT_BY_HIGHER_PRIORITY_TASKS (Feasible blocks: BLK-CK-NIGHT-01, BLK-CK-NIGHT-02)"],
    "TASK-TRD-004": ["COMPETED_OUT_BY_HIGHER_PRIORITY_TASKS (Feasible blocks: BLK-NG-NIGHT-01)"],
    "TASK-TRD-005": ["COMPETED_OUT_BY_HIGHER_PRIORITY_TASKS (Feasible blocks: BLK-KP-NIGHT-01, BLK-KP-NIGHT-02)"]
  },
  "solver_wall_time_seconds": 0.04
}
```

---

### 6.2 Switch Dataset Scope
- **Method:** `POST`
- **Path:** `/api/datasets/switch`
- **Request Body:**
```json
{
  "dataset_type": "full_dataset"
}
```
*(Options: `"demo_fixture"` or `"full_dataset"`)*
- **Response (`200 OK`):**
```json
{
  "active_dataset": "full_dataset",
  "description": "Scaled ~200-task synthetic dataset across 12 railway trunks.",
  "task_count": 200,
  "critical_task_count": 30,
  "block_count": 48,
  "train_count": 48,
  "corridor_count": 12,
  "corridors": ["ADI-BRC", "BPL-ET", "CSTM-KYN", "HWH-BWN", "KYN-PUN", "LKO-CNB", "MAS-AJJ", "NDLS-GZB", "NGP-WR", "PNBE-MGS", "SBC-JTJ", "SEC-KZJ"],
  "departments": ["ENGINEERING", "S&T", "TRD"]
}
```

# DATA CONTRACT

This document is the canonical interface between data generation, optimization, backend and frontend.

## MaintenanceTask

```json
{
  "task_id": "ENG_001",
  "department": "ENGINEERING",
  "asset_id": "TRK_1001",
  "asset_type": "TRACK",
  "corridor_id": "C01",
  "location_start_km": 120.4,
  "location_end_km": 121.1,
  "direction": "DOWN",
  "defect_type": "TRACK_GEOMETRY",
  "severity": 8,
  "criticality": 9,
  "safety_risk": 9,
  "overdue_days": 12,
  "estimated_duration_minutes": 90,
  "required_crew_count": 6,
  "required_resources": ["TRACK_TEAM"],
  "precedence_task_ids": [],
  "earliest_start": "2026-08-27T00:00:00",
  "deadline": "2026-08-29T23:59:00",
  "status": "PENDING"
}
```

## TrainMovement

```json
{
  "train_id": "T12123",
  "corridor_id": "C01",
  "train_type": "EXPRESS",
  "direction": "UP",
  "start_time": "2026-08-27T02:15:00",
  "end_time": "2026-08-27T02:45:00",
  "operational_priority": 10
}
```

## GoodsForecast

```json
{
  "corridor_id": "C01",
  "window_start": "2026-08-27T02:00:00",
  "window_end": "2026-08-27T03:00:00",
  "expected_goods_trains": 2,
  "probability": 0.7,
  "traffic_density_score": 78
}
```

## BlockWindow

```json
{
  "block_id": "B001",
  "corridor_id": "C01",
  "start_time": "2026-08-27T02:00:00",
  "end_time": "2026-08-27T04:00:00",
  "max_concurrent_teams": 3,
  "available_capacity_minutes": 120,
  "safety_class": "STANDARD",
  "permitted_departments": ["ENGINEERING", "SNT", "TRD"],
  "traffic_density_score": 20
}
```

## Schedule result

```json
{
  "task_id": "ENG_001",
  "block_id": "B001",
  "scheduled_start": "2026-08-27T02:00:00",
  "scheduled_end": "2026-08-27T03:30:00",
  "status": "SCHEDULED",
  "explanation": {
    "priority": "CRITICAL",
    "selected_window_reason": [
      "LOW_TRAFFIC_COST",
      "SAME_CORRIDOR_AS_2_OTHER_TASKS",
      "WITHIN_DEADLINE"
    ]
  }
}
```

## Enums

Department:
- ENGINEERING
- SNT
- TRD

Task status:
- PENDING
- SCHEDULED
- COMPLETED
- CANCELLED

Priority:
- ROUTINE
- IMPORTANT
- HIGH
- CRITICAL

Do not add arbitrary fields to the core model without documenting them.

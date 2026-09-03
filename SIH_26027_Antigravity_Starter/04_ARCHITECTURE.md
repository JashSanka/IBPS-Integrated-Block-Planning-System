# ARCHITECTURE

## High-level

```text
┌───────────────────────────────────────────────────────────┐
│                    DATA SOURCES                           │
│ TMS │ SMMS │ TDMS │ COA │ Train Timetable │ Goods Forecast│
└──────────────────────────┬────────────────────────────────┘
                           ↓
                 Adapter / Ingestion Layer
                           ↓
                  Unified Domain Model
                           ↓
          ┌────────────────┴────────────────┐
          ↓                                 ↓
  Priority Engine                    Block Opportunity
          │                            / Conflict Model
          └────────────────┬────────────────┘
                           ↓
                  CP-SAT Optimizer
                           ↓
                 Baseline Comparison
                           ↓
                   Metrics Engine
                           ↓
                       FastAPI
                           ↓
                    React Dashboard
```

## Repository

```text
backend/
  app/
    domain/
    data/
    scoring/
    optimization/
    metrics/
    adapters/
    api/
    config.py
    main.py

tests/
  unit/
  integration/
  fixtures/

frontend/
  src/
    components/
    pages/
    api/
    types/

data/
  raw/
  generated/
  fixtures/

docs/
```

## Dependency direction

Allowed:

UI → API → application/domain → optimizer/scoring/data

Not allowed:

optimizer → React
domain → API framework
React → CSV files
UI → direct solver calls

## Adapter interfaces

Define:

```python
class TMSAdapter(Protocol): ...
class SMMSAdapter(Protocol): ...
class TDMSAdapter(Protocol): ...
class COAAdapter(Protocol): ...
```

Synthetic implementations should satisfy these interfaces.

## Optimizer boundary

Preferred interface:

```python
result = optimizer.generate_plan(
    tasks=tasks,
    blocks=blocks,
    trains=trains,
    goods_forecasts=goods_forecasts,
    resources=resources,
    horizon=horizon,
    weights=weights,
)
```

Return a typed PlanResult.

The optimizer must be testable without FastAPI or React.

## Configuration

Put:
- scoring weights;
- solver time limit;
- objective penalties;
- demo seed;
- planning horizon

in configuration, not scattered constants.

## Logging

Log:
- dataset size;
- candidate assignments;
- solver status;
- objective;
- runtime;
- scheduled/unscheduled counts;
- warnings.

Never log sensitive credentials.

# BUILD PLAN — AUG 26 TO AUG 29

## Milestone 0 — Repository audit

Agent:
- inspect current repository;
- read all docs;
- identify tech stack;
- do not overwrite existing work.

Deliver:
- implementation plan;
- directory structure.

## Milestone 1 — Data + domain

Deliver:
- Pydantic models;
- synthetic generator;
- deterministic fixture;
- adapter interfaces.

Acceptance:
- 20–40 fixture tasks;
- all 3 departments;
- multiple corridors;
- trains;
- blocks;
- goods forecast;
- deliberate conflicts.

## Milestone 2 — Priority

Deliver:
- normalized priority formula;
- configurable weights;
- explanation breakdown.

Acceptance:
- critical task ranks above routine task in expected scenario;
- tests for scoring.

## Milestone 3 — Baseline

Deliver:
- deterministic naive scheduler.

Acceptance:
- generates a plan;
- measurable metrics.

## Milestone 4 — CP-SAT

Deliver:
- candidate generation;
- variables;
- hard constraints;
- objective;
- result object.

Acceptance:
- no illegal assignments;
- tasks are not double-scheduled;
- resource limits hold;
- precedence holds;
- clubbing works;
- high-cost train conflicts are avoided.

## Milestone 5 — Evaluation

Deliver:
- baseline vs optimized metrics.

Acceptance:
- optimizer demonstrates improvement on designed fixture.

## Milestone 6 — API

Deliver:
- health;
- data endpoints;
- plan generation;
- plan retrieval;
- metrics;
- emergency what-if.

Acceptance:
- API can execute an end-to-end plan.

## Milestone 7 — UI

Deliver:
- KPIs;
- task table;
- Gantt;
- baseline vs optimized;
- explanations;
- what-if.

Acceptance:
- a non-developer can understand the demo.

## Milestone 8 — Reliability

Deliver:
- tests;
- deterministic seed;
- error handling;
- fallback demo data;
- README;
- run instructions.

## Milestone 9 — Optional ML

Only after everything above works.

Potential:
- synthetic historical asset records;
- failure/service-impact target;
- Gradient Boosting/XGBoost;
- evaluate using holdout data;
- expose failure risk as one input to priority scoring.

If this destabilizes the system, remove it from the demo.

## Final demo sequence

1. Show independent departmental requests.
2. Show conflicts/wasted windows.
3. Show priorities.
4. Generate plan.
5. Show clubbed cross-department block.
6. Show avoided train conflict.
7. Show KPI comparison.
8. Add emergency defect.
9. Re-plan.
10. Show changed plan and explanation.

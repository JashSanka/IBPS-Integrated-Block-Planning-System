# AGENT RULES — READ BEFORE CODING

## Rule 1 — Understand before changing

Inspect the repository before editing.
Never assume an empty repository if files exist.

## Rule 2 — The optimizer is the source of truth

The frontend must never invent schedules.
Demo schedules must never be hardcoded as if they were optimizer results.

## Rule 3 — No fake integrations

Do not create fake "live Railway API" claims.
Adapters are allowed.
Synthetic adapters are expected.

## Rule 4 — No fake AI

A deterministic priority formula is acceptable.
A synthetic ML model is acceptable only if its training/evaluation is real and documented.
Do not call a weighted formula "machine learning."

## Rule 5 — Optimization before aesthetics

If forced to choose:
working optimizer > API polish > dashboard polish.

## Rule 6 — Safety beats objective value

Never allow an optimization objective to override a hard safety constraint.

## Rule 7 — Explain every recommendation

A schedule should be explainable:
- why task was prioritized;
- why block was selected;
- why another block was rejected;
- what conflicts were avoided.

## Rule 8 — Deterministic demo

Use fixed random seeds.
The same demo input should generate reproducible results.

## Rule 9 — Incremental development

After every major feature:
- run unit tests;
- run integration test;
- inspect output.

## Rule 10 — Avoid overengineering

Do not introduce:
- microservices;
- message queues;
- Kubernetes;
- authentication;
- cloud infrastructure;
- distributed optimization

unless explicitly required.

## Rule 11 — Keep assumptions documented

If the official problem statement does not specify a field or rule, label it as a prototype assumption.

## Rule 12 — Do not overclaim metrics

Simulation results must say:
"on our synthetic/demo dataset."

Never say:
"Indian Railways will achieve X% improvement."

## Rule 13 — Human-in-the-loop

The system recommends a plan.
An authorized planner can approve/override it.

## Rule 14 — Preserve architecture boundaries

Data ingestion → domain model → scoring → optimization → metrics → API → UI.

Do not move business logic into React components.

## Rule 15 — Stop and report if a core assumption is invalid

Do not silently build around a broken optimization model.
Document:
- what failed;
- why;
- chosen fix;
- effect on constraints.

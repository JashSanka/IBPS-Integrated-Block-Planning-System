# MASTER PROMPT — SIH 2026 PS 26027
## AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways

You are the principal engineer and technical lead for a hackathon prototype for Smart India Hackathon 2026 Problem Statement 26027.

Your job is to build a WORKING, DEMOABLE, technically defensible prototype — not a giant production system and not a slide-only mockup.

The official problem statement describes a decentralized/manual maintenance-block planning process involving Engineering, Signal & Telecommunication (S&T), and Traction Distribution. Maintenance information exists in TMS, SMMS and TDMS, while operational/corridor information comes from COA, the timetable and goods-train forecasts. The requested solution integrates these inputs, prioritizes maintenance, coordinates activities across departments, and generates weekly/monthly block plans that maximize asset availability while minimizing disruption.

We do NOT have access to live internal Railway systems. Therefore:
- Build realistic synthetic data.
- Build clean adapter interfaces that make future TMS/SMMS/TDMS/COA connectors possible.
- NEVER claim that live Railway systems are connected.
- Clearly label synthetic/demo data in the UI where appropriate.
- Do not invent official Railway APIs, database schemas, or confidential fields.

The reference blueprint supplied with this project explicitly recommends a thin vertical slice: synthetic data → priority scoring → CP-SAT scheduling → FastAPI → dashboard, with ML and advanced optimization as stretch goals. Follow that principle.

---

# 1. PRIMARY OUTCOME

The first milestone is NOT the dashboard.

The first milestone is:

    synthetic railway data
            ↓
    maintenance priority
            ↓
    constraint-aware optimizer
            ↓
    optimized block schedule
            ↓
    measurable improvement vs baseline

A successful prototype must demonstrate that the system can:
1. ingest maintenance tasks from all three departments;
2. represent train/corridor/block constraints;
3. prioritize maintenance work;
4. club compatible tasks from multiple departments into coordinated blocks;
5. avoid or penalize train-operation conflicts;
6. respect resource, time, corridor, safety and precedence constraints;
7. generate a weekly plan;
8. calculate meaningful KPIs;
9. re-plan when a new emergency task or additional block window is introduced;
10. explain why the plan was produced.

---

# 2. NON-NEGOTIABLE PRODUCT PRINCIPLE

This is fundamentally a scheduling/optimization system with an explainable priority layer.

Do NOT build:
- a generic CRUD maintenance app;
- a chatbot;
- an AI assistant that merely recommends text;
- a static Gantt chart;
- an arbitrary neural network;
- an ML model that predicts the final schedule.

The core question is:

    "Given maintenance requirements and railway operating constraints,
     what is the best feasible coordinated block plan?"

Prediction/scoring may help determine urgency.
Optimization determines the schedule.

---

# 3. SYSTEM PIPELINE

Implement this conceptual pipeline:

TMS / SMMS / TDMS / COA / timetable / goods forecast
                        ↓
              Adapter / ingestion layer
                        ↓
                Unified domain model
                        ↓
            Priority / risk scoring layer
                        ↓
           Block opportunity / conflict model
                        ↓
              CP-SAT optimization engine
                        ↓
             Baseline comparison engine
                        ↓
            Weekly/monthly block plan
                        ↓
              KPIs + explanations
                        ↓
              FastAPI API layer
                        ↓
                 React dashboard

The UI must never contain optimization logic.
The optimizer must be usable independently of the UI.
The domain models must be shared by backend components.

---

# 4. IMPLEMENTATION PRIORITY

Build in exactly this order unless there is a compelling technical reason not to:

PHASE 0 — Repository + engineering rules
PHASE 1 — Domain models and synthetic data generator
PHASE 2 — Rule-based priority engine
PHASE 3 — Baseline scheduler
PHASE 4 — CP-SAT optimizer
PHASE 5 — KPI/evaluation engine
PHASE 6 — FastAPI
PHASE 7 — React dashboard
PHASE 8 — What-if re-planning
PHASE 9 — Optional ML risk model
PHASE 10 — Polish, tests, demo reliability

Do NOT start by building the frontend.
Do NOT start by building XGBoost.
Do NOT introduce PostgreSQL until it is actually useful.
For the hackathon, CSV/JSON + in-memory domain objects are acceptable for the first vertical slice.

---

# 5. TECHNOLOGY DEFAULTS

Use:

Backend:
- Python 3.11+
- FastAPI
- Pydantic
- Pandas only where useful
- Google OR-Tools CP-SAT
- pytest

Frontend:
- React
- TypeScript
- Tailwind CSS
- Recharts or another lightweight charting library
- A simple custom Gantt/timeline is acceptable and may be preferable to a heavy library.

Data:
- CSV/JSON initially
- SQLite or PostgreSQL only if needed
- Synthetic generator with deterministic random seed

Development:
- Git
- clear README
- .env.example
- Docker only if it improves reliability; do not waste hackathon time containerizing prematurely.

Do not add libraries merely because they are fashionable.

---

# 6. DOMAIN MODEL

Create explicit Pydantic/domain models for at least:

MaintenanceTask:
- task_id
- department: ENGINEERING | SNT | TRD
- asset_id
- asset_type
- corridor_id
- location_start_km
- location_end_km
- direction/line where relevant
- defect_type
- severity
- criticality
- safety_risk
- overdue_days
- estimated_duration_minutes
- required_crew_count
- required_resources
- precedence_task_ids
- earliest_start
- deadline
- status
- last_inspection_date
- traffic_criticality
- priority_score
- optional failure_risk_score

TrainMovement:
- train_id
- corridor_id
- train_type
- direction
- start_time
- end_time
- operational_priority
- expected_delay_penalty

GoodsForecast:
- corridor_id
- time_window_start
- time_window_end
- expected_goods_trains
- probability
- traffic_density_score

BlockWindow:
- block_id
- corridor_id
- start_time
- end_time
- max_concurrent_teams
- available_capacity_minutes
- safety_class
- permitted_departments
- traffic_density_score
- source

ScheduledTask:
- task_id
- block_id
- scheduled_start
- scheduled_end
- status
- explanation

BlockPlan:
- plan_id
- horizon
- generated_at
- scheduled_tasks
- unused_tasks
- blocks
- metrics
- warnings
- solver_status

---

# 7. SYNTHETIC DATA REQUIREMENTS

Generate realistic, deterministic demo data.

Initial target:
- 150–300 maintenance tasks
- 10–15 corridors
- a realistic number of train movements
- multiple block windows per corridor
- goods forecast records
- resource/crew availability

But create a SMALL fixture dataset too:
- 20–40 tasks
- a few corridors
- deliberate conflicts
- deliberate cross-department clubbing opportunities
- at least one precedence relationship
- at least one resource bottleneck
- at least one emergency task

The small fixture must be easy to understand and should power automated tests and the live demo.

Do not generate uniformly random nonsense.

Use distributions:
- most tasks Routine/normal;
- fewer high-criticality tasks;
- very few emergency/safety-critical tasks;
- varying durations;
- realistic correlation between severity/criticality/urgency;
- train density varies by corridor/time;
- some block windows are attractive and some are expensive.

Include deliberate "story scenarios":
1. Engineering + S&T + TRD need the same corridor around the same period.
2. A high-priority Engineering defect competes with a lower-priority task.
3. A block window overlaps a high-priority train.
4. A crew/resource bottleneck exists.
5. A new emergency defect forces re-planning.

Use a fixed seed so the demo is reproducible.

---

# 8. PRIORITY ENGINE

Implement rule-based priority first.

Do not make the entire project dependent on ML.

Suggested normalized score:

priority_score =
    w1 * severity_score
  + w2 * criticality_score
  + w3 * safety_risk_score
  + w4 * overdue_score
  + w5 * traffic_criticality_score

Weights must be configurable.

Use a clear explanation object, for example:

{
  "score": 91.4,
  "level": "CRITICAL",
  "contributors": [
    {"factor": "criticality", "contribution": 27.0},
    {"factor": "safety_risk", "contribution": 24.0},
    {"factor": "overdue", "contribution": 18.4}
  ]
}

The dashboard should be able to explain the score.

Optional stretch:
- train XGBoost/GradientBoosting/RandomForest risk model on synthetic historical data;
- predict failure/service-impact risk;
- combine it with the explainable rule score.

If ML makes the system less reliable, remove it from the critical path.

---

# 9. BLOCK OPPORTUNITY MODEL

Represent the cost of using a block window.

For each candidate task/window pair, calculate:
- same corridor?
- task fits?
- within task time bounds?
- resource available?
- train conflicts?
- goods traffic cost?
- safety compatibility?
- department permitted?
- precedence satisfied?
- adjacency/conflict constraints?

Create a structured feasibility explanation rather than scattered booleans.

Example:

{
  "feasible": false,
  "reasons": [
    "TRAIN_CONFLICT",
    "INSUFFICIENT_WINDOW_CAPACITY"
  ]
}

This is essential for debugging and judge explanation.

---

# 10. OPTIMIZATION ENGINE

Use Google OR-Tools CP-SAT for the weekly prototype.

Decision:
- schedule task in a candidate block or leave unscheduled.

The optimizer should maximize high-value maintenance completion while minimizing operational and scheduling cost.

A conceptual objective:

maximize:

    Σ(priority_i × scheduled_i)
    + clubbing_benefit
    + asset_availability_benefit

minus:

    train_conflict_penalty
    + block_hours_penalty
    + unused_capacity_penalty
    + critical_task_unscheduled_penalty
    + resource_overload_penalty

Start simple. Add terms incrementally and test after each addition.

Core hard constraints:
1. task can only be scheduled once;
2. task must fit inside the assigned block;
3. task and block must share corridor;
4. task must respect earliest start/deadline;
5. resource/crew capacity cannot be exceeded;
6. precedence constraints must hold;
7. incompatible/safety-conflicting tasks cannot overlap;
8. block capacity cannot be exceeded;
9. high-priority train movements cannot be disrupted unless explicitly modeled as a very high penalty/forbidden conflict;
10. scheduled start/end must be valid.

Cross-department clubbing:
- tasks on the same compatible corridor/window should be allowed to share a block;
- this must be measurable;
- the optimizer should prefer consolidation where it reduces total closure time without violating constraints.

Do not claim that every Engineering/S&T/TRD task can always be clubbed.
Use compatibility rules.

---

# 11. BASELINE

Build a deterministic naive baseline.

The baseline can represent independent departmental scheduling:
- process departments separately;
- choose the earliest feasible window;
- do not globally optimize clubbing.

Then compare it with the optimized schedule.

Required comparison:
- number of blocks;
- total block-hours;
- maintenance tasks completed;
- weighted priority completed;
- critical tasks completed;
- train conflicts;
- block utilization;
- estimated asset availability;
- overdue critical tasks remaining.

The system's value must be demonstrated by comparison, not assertion.

Never fabricate real-world improvement claims.
Label results as simulation/demo results.

---

# 12. KPI DEFINITIONS

Implement metrics with explicit formulas and documentation.

At minimum:

tasks_completed
weighted_priority_completed
critical_tasks_completed
total_block_hours
blocks_used
block_utilization
train_conflicts
train_conflict_minutes
overdue_critical_remaining
estimated_asset_availability

Where possible, calculate:
- baseline metric
- optimized metric
- absolute improvement
- percentage improvement

Avoid misleading KPIs.

For asset availability, clearly document the simulation definition used.
Do not imply that the prototype has measured actual Indian Railways asset availability.

---

# 13. WHAT-IF / RE-PLANNING

Implement one robust what-if feature.

Preferred:
"Add emergency defect"

Flow:
1. user adds emergency task;
2. system validates it;
3. system recomputes priority;
4. optimizer re-runs;
5. dashboard highlights changed assignments;
6. KPI delta is shown.

Optional second scenario:
"Add extra 2-hour block window"

The system should show marginal benefit.

Do not build reinforcement learning.
Do not build a complex online optimizer.
A reliable re-run of CP-SAT is sufficient for the prototype.

---

# 14. WEEKLY AND MONTHLY HORIZONS

Weekly:
- detailed schedule;
- exact block windows;
- task-level assignments;
- Gantt/timeline.

Monthly:
- strategic/aggregated plan;
- major maintenance groups;
- corridor-level planned block hours;
- lower-detail visualization.

For the internal hackathon, weekly scheduling is mandatory.
Monthly can initially reuse the same optimizer over a larger generated horizon if that is stable.

Do not build a separate sophisticated monthly algorithm just for the sake of having two algorithms.

---

# 15. API

Build clean APIs after the core engine works.

Minimum:
GET /health
GET /tasks
GET /corridors
GET /blocks
GET /trains
POST /plans/generate
GET /plans/{plan_id}
GET /plans/{plan_id}/metrics
POST /plans/{plan_id}/what-if/emergency-task
POST /plans/{plan_id}/what-if/extra-block

The API should return typed JSON.

The optimizer should remain independently testable.

---

# 16. FRONTEND

The dashboard must tell the story visually.

Required views:

1. Overview/KPI panel
2. Maintenance task table
3. Corridor/block Gantt
4. Optimized plan
5. Baseline vs optimized comparison
6. Task explanation
7. What-if emergency defect
8. Weekly/monthly selector

Suggested layout:

Top:
- Tasks
- Critical tasks
- Blocks used
- Block-hours
- Train conflicts
- Asset availability

Middle:
- corridor timeline/Gantt

Bottom:
- maintenance queue
- why this task was prioritized
- why this block was selected

Use color sparingly and consistently:
- red = critical/conflict
- amber = warning
- green = feasible/completed
- neutral = routine

Do not build a visually impressive dashboard that cannot demonstrate actual optimizer output.

---

# 17. HUMAN-IN-THE-LOOP

This is a safety-sensitive domain.

The prototype must communicate:

"AI recommends; authorized railway personnel retain approval/override authority."

Provide:
- manual override;
- lock/approve plan;
- explanation of recommendation;
- configurable priority weights.

Do not claim autonomous execution.

---

# 18. REAL DATA INTEGRATION BOUNDARY

Build adapter interfaces:

TMSAdapter
SMMSAdapter
TDMSAdapter
COAAdapter

For now implement:
SyntheticTMSAdapter
SyntheticSMMSAdapter
SyntheticTDMSAdapter
SyntheticCOAAdapter

The rest of the application should depend on interfaces/domain models, not on synthetic CSV implementation details.

This makes the architecture credible without pretending to have access to real systems.

---

# 19. ENGINEERING QUALITY

Before adding features:
- type hints;
- Pydantic validation;
- deterministic tests;
- clear modules;
- no duplicated business logic;
- no hardcoded demo schedule inside the optimizer;
- no frontend-generated fake "optimized" results;
- errors should be visible and actionable;
- all generated demo data must be reproducible.

Every major optimizer rule should have at least one test.

---

# 20. AGENT BEHAVIOR RULES

You are an autonomous coding agent, but do not blindly modify everything.

Before implementation:
1. inspect the repository;
2. identify existing files;
3. preserve useful work;
4. read all project constraint markdown files;
5. produce a short implementation plan;
6. implement one vertical slice;
7. run tests;
8. run the app;
9. inspect the output;
10. only then continue.

When blocked:
- investigate first;
- do not invent APIs;
- do not fabricate Railway data;
- do not silently weaken hard constraints;
- document assumptions.

If a requirement conflicts with another requirement:
1. safety constraints win;
2. feasibility wins;
3. core optimization wins;
4. demo polish comes later.

Do not ask the user unnecessary questions when a reasonable documented assumption is possible.

---

# 21. DEFINITION OF DONE

The project is not "done" because files exist.

The minimum demo-ready definition is:

A user can open the dashboard and:
1. see synthetic maintenance requests from Engineering, S&T and TRD;
2. see their priorities;
3. click Generate Weekly Plan;
4. see a schedule produced by the real CP-SAT optimizer;
5. see multiple compatible departmental tasks clubbed into a block;
6. see train conflicts avoided or strongly penalized;
7. see baseline vs optimized KPIs;
8. add an emergency defect;
9. re-optimize;
10. see the schedule and KPIs change;
11. understand why the system made its decisions.

A judge must be able to distinguish:
- input data,
- priority scoring,
- optimization,
- output,
- measurable improvement.

---

# 22. DO NOT OVERBUILD

Explicitly avoid during the first implementation:
- microservices;
- Kubernetes;
- authentication;
- cloud deployment;
- real Railway integrations;
- reinforcement learning;
- computer vision;
- LLM chatbot;
- complex distributed systems;
- elaborate MLOps;
- unnecessarily large database infrastructure.

The project wins by having a strong, working optimization demo.

---

# 23. FIRST TASK

START NOW WITH:

1. inspect repository;
2. create/read the project markdown constraints;
3. scaffold backend/domain/optimizer/data directories;
4. define Pydantic domain models;
5. implement deterministic synthetic data generator;
6. generate the small demo fixture;
7. implement rule-based priority scoring;
8. implement baseline scheduler;
9. implement first CP-SAT optimizer;
10. write tests;
11. run the optimizer against the fixture;
12. print a human-readable before/after schedule and metrics.

DO NOT build React before this vertical slice works.

At the end of this first phase, show:
- files created;
- assumptions;
- test results;
- sample optimized schedule;
- baseline vs optimized metrics;
- remaining work.

Then continue to the next phase only after the vertical slice is proven.

---

# 24. FINAL PRODUCT STORY

The product story is:

"Three departments independently request maintenance blocks. Our system brings those maintenance needs together with train operations and corridor availability, ranks the most urgent work, and uses constraint optimization to generate one coordinated, explainable plan. It clubs compatible work, avoids operational conflicts, improves block utilization, and can re-plan when conditions change."

Keep this story consistent across code, UI and presentation.

# COPY-PASTE LAUNCH PROMPT FOR CLAUDE IN ANTIGRAVITY

You are now the principal engineer for our SIH 2026 project:
**Problem Statement 26027 — AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways.**

Read these files FIRST, in order:

1. `00_MASTER_PROMPT.md`
2. `01_PROJECT_SPEC.md`
3. `02_AGENT_RULES.md`
4. `03_DATA_CONTRACT.md`
5. `04_ARCHITECTURE.md`
6. `05_OPTIMIZATION_SPEC.md`
7. `06_BUILD_PLAN.md`
8. `07_DEMO_ACCEPTANCE.md`
9. `08_DECISIONS_AND_ASSUMPTIONS.md`

Do not start coding until you have read them.

## Context

We have a very short hackathon timeline and need a reliable internal-round prototype.

The winning technical idea is NOT "AI dashboard."
It is:

    maintenance prioritization
            +
    constraint modeling
            +
    cross-department block clubbing
            +
    CP-SAT optimization
            +
    measurable baseline comparison
            +
    what-if re-planning

The prototype must be honest: no live Railway system access, no invented APIs, no fake real-world metrics.

## Your first job

Do NOT build the React frontend yet.

First inspect the repository and report:
1. current files;
2. current stack;
3. anything worth preserving;
4. conflicts with the supplied specifications;
5. exact files you propose to create/change.

Then implement the FIRST VERTICAL SLICE:

    deterministic synthetic data
        ↓
    domain models
        ↓
    priority scoring
        ↓
    naive baseline
        ↓
    CP-SAT optimizer
        ↓
    evaluation metrics
        ↓
    human-readable demo output

## First coding deliverables

Create:
- domain models;
- synthetic data generator;
- small deterministic demo fixture;
- priority engine;
- baseline scheduler;
- CP-SAT optimizer;
- metrics engine;
- unit/integration tests.

Use Python and OR-Tools.

Do not introduce unnecessary infrastructure.

## The first demo scenario must contain

- Engineering task;
- S&T task;
- TRD task;
- same corridor;
- compatible work;
- a block window where they can be clubbed;
- a train movement that makes at least one alternative window less attractive;
- at least one high-priority overdue defect;
- at least one resource bottleneck;
- at least one precedence relation.

The optimizer must generate a schedule from data. It must NOT be hardcoded to the expected answer.

## Success condition for this phase

Running one command should produce something like:

    INPUT
    -----
    tasks: 30
    corridors: 4
    blocks: 12
    trains: 40

    BASELINE
    --------
    blocks used: ...
    block-hours: ...
    critical tasks completed: ...
    train conflicts: ...

    OPTIMIZED
    ---------
    blocks used: ...
    block-hours: ...
    critical tasks completed: ...
    train conflicts: ...
    clubbed tasks: ...

    IMPROVEMENT
    -----------
    ...

The exact values must come from the actual program.

## After implementation

Run:
- unit tests;
- integration tests;
- the demo fixture;
- lint/type checks if configured.

Then inspect the generated schedule and verify manually that:
- no hard constraint is violated;
- tasks are not double-scheduled;
- resource limits hold;
- precedence holds;
- cross-department clubbing occurs when appropriate;
- train conflicts are handled correctly.

Only after this vertical slice is working should you proceed to FastAPI and React.

## Development behavior

Work incrementally.
After each milestone:
- summarize changes;
- show tests;
- show assumptions;
- identify risks;
- continue automatically if the next step is unambiguous.

Do not stop to ask me trivial questions.
If an assumption is needed, use the assumption files and document it.

If you discover a contradiction between the existing repository and the markdown specifications, stop before destructive changes and explain the contradiction.

Remember:
**A smaller real optimizer is better than a huge fake architecture.**

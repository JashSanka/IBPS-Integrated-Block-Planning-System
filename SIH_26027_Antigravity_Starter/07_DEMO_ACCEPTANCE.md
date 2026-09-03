# DEMO ACCEPTANCE CRITERIA

The internal hackathon demo is successful only if all mandatory scenarios pass.

## Scenario A — Cross-department clubbing

Input:
- Engineering task on C01
- S&T task on C01
- TRD task on C01
- compatible timing
- one suitable block

Expected:
- all are scheduled in one coordinated block where capacity/safety permit;
- fewer closure hours than naive independent scheduling.

## Scenario B — Train conflict

Input:
- attractive block overlaps a high-priority train;
- another lower-traffic window exists.

Expected:
- optimizer chooses the safer/lower-disruption option.

## Scenario C — Priority

Input:
- critical overdue defect;
- routine non-overdue task.

Expected:
- critical task receives materially higher priority.

## Scenario D — Resource bottleneck

Input:
- two tasks require the same limited crew.

Expected:
- they are not illegally scheduled concurrently.

## Scenario E — Precedence

Input:
- task B requires task A.

Expected:
- B cannot be scheduled before A.

## Scenario F — Emergency

Input:
- new safety-critical task.

Expected:
- priority is high;
- re-plan changes schedule;
- existing hard constraints remain valid;
- UI shows what changed.

## Scenario G — Baseline comparison

Expected dashboard shows:
- blocks used;
- total block-hours;
- tasks completed;
- weighted priority;
- critical tasks;
- train conflicts;
- block utilization;
- asset availability proxy.

All figures must be generated from actual program output.

## Judge trust

The demo must explicitly state:
- data is synthetic;
- architecture is designed for future adapters;
- AI recommends;
- human approval remains required;
- KPI improvements are simulation results.

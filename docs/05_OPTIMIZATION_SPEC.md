# OPTIMIZATION SPECIFICATION

## Goal

Generate the highest-value feasible maintenance plan.

## Decision variable

For each maintenance task i and candidate block j:

x[i,j] = 1 if task i is assigned to block j.

A task may remain unscheduled.

## Candidate generation

Only create candidate task-block pairs when:
- corridor matches;
- department is permitted;
- task duration can fit;
- time bounds intersect;
- basic safety requirements are compatible.

This reduces solver size.

## Hard constraints

### Task uniqueness

For every task:

sum(x[i,j]) <= 1

### Block capacity

Do not exceed available work capacity.

### Crew/resource capacity

Do not exceed available crew/resources.

### Time

scheduled_start >= earliest_start
scheduled_end <= deadline

### Precedence

If task B depends on task A:

start(B) >= end(A)

### Safety

Conflicting tasks may not overlap.

### Corridor

Task must be scheduled only on its corridor.

## Soft penalties

Use carefully weighted penalties:
- train conflict;
- goods traffic;
- unnecessary block duration;
- fragmentation;
- unused capacity;
- unscheduled critical work.

## Clubbing

Clubbing is not simply "same corridor = same block."

A pair/group is club-compatible only if:
- same/compatible corridor;
- time-compatible;
- resource-compatible;
- safety-compatible;
- permitted department combination;
- no conflicting equipment requirement.

The benefit of clubbing should reward reducing closure/block overhead.

## Objective design

Start:

maximize weighted completed priority

Then add:
1. critical-task completion;
2. train disruption penalty;
3. block-hours penalty;
4. clubbing benefit;
5. unused capacity penalty.

Do not add ten objective terms at once.
Validate each increment.

## Solver

Weekly:
- CP-SAT
- configurable time limit
- return best feasible solution if optimality is not reached

Monthly:
- initially use the same CP-SAT architecture with a larger time limit or aggregation;
- only introduce metaheuristics if the actual prototype needs them.

Do NOT build a genetic algorithm just because the architecture diagram mentions one.

## Solver result must include

- status;
- objective value;
- runtime;
- assignments;
- unscheduled tasks;
- constraint/diagnostic warnings.

## Failure behavior

If no feasible plan exists:
- return partial best feasible plan if available;
- identify unscheduled tasks;
- provide reasons where possible;
- never silently return an empty schedule.

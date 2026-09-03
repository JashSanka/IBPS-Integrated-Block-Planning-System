# PROJECT SPECIFICATION — PS 26027

## Purpose

This document defines WHAT the prototype is solving.

## Problem

Indian Railways maintenance requirements from:
- Engineering
- Signal & Telecommunication (S&T)
- Traction Distribution (TRD)

are described in the problem statement as being maintained/planned through separate systems/processes, while operational constraints are available through the Control Office/timetable/goods forecast.

The prototype creates a coordinated planning layer.

## Inputs

### Maintenance
- task
- department
- asset
- corridor/location
- defect
- severity
- criticality
- safety risk
- overdue days
- duration
- crew/resources
- precedence
- time bounds

### Operations
- train movements
- train priority
- corridor
- goods forecast
- block windows
- corridor traffic density

## Outputs

For each planning run:
- scheduled tasks
- unscheduled tasks
- assigned block
- start/end time
- reason
- conflict warnings
- KPIs

## Core business question

"What is the best feasible coordinated maintenance block plan for the chosen horizon?"

## Optimization goals

Primary:
1. maximize completion of high-priority maintenance;
2. minimize unnecessary closure/block hours;
3. minimize train-operation disruption;
4. consolidate compatible departmental work;
5. maximize estimated asset availability.

Secondary:
- improve block utilization;
- reduce overdue critical work;
- avoid unnecessary schedule churn during re-planning.

## Hard vs soft constraints

### Hard
- corridor compatibility;
- time window;
- task duration;
- resource availability;
- precedence;
- safety incompatibility;
- block capacity;
- task scheduled at most once.

### Soft
- train conflict where the scenario explicitly allows penalty;
- goods traffic cost;
- block fragmentation;
- unused capacity;
- lower-priority task omission.

Safety-critical conflicts should normally be hard constraints.

## Important terminology

Use:
- maintenance task
- asset
- corridor/section
- block window
- block plan
- department
- priority
- train conflict
- resource
- re-planning

Do not invent official Railway terminology when the source material does not establish it.

## Prototype boundary

This is a simulation/prototype:
- no live TMS access;
- no live SMMS access;
- no live TDMS access;
- no live COA access.

Synthetic data must be explicitly identified as such.

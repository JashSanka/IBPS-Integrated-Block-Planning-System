# DECISIONS AND ASSUMPTIONS — IBPS PS 26027

This file is a living record of architectural decisions, modeling choices, and mathematical formulas implemented in the Integrated Block Planning System (IBPS).

---

## 1. Confirmed from the SIH Problem Statement (PS 26027)

- **Departments:** Engineering (Track/Structures), Signal & Telecommunication (S&T), Traction Distribution (TRD / OHE).
- **Legacy Boundaries:** Maintenance requirements originate in departmental systems (TMS, SMMS, TDMS) and are currently siloed.
- **Operational Data:** Control Office Application (COA) / Train Timetable / Freight Forecast provides corridor traffic constraints and block window opportunities.
- **Goal:** Automated, conflict-free, cross-department integrated block planning maximizing asset availability and minimizing operational disruption.
- **Horizons:** Tactical Weekly detailed planning and Strategic Monthly aggregated planning.

---

## 2. Mathematical Modeling Decisions

### 2.1 Explainable Priority Scoring (Rule-Based)
- **Formula:**
  $$\text{Priority Score} = w_1 \cdot \text{Severity}_{\text{norm}} + w_2 \cdot \text{Criticality}_{\text{norm}} + w_3 \cdot \text{SafetyRisk}_{\text{norm}} + w_4 \cdot \text{OverdueScore}_{\text{norm}} + w_5 \cdot \text{TrafficCriticality}_{\text{norm}}$$
- **Default Weights:**
  - $w_1 = 0.25$ (Defect Severity: Critical=100, Major=75, Minor=45, Routine=20)
  - $w_2 = 0.25$ (Asset Criticality: 0–100)
  - $w_3 = 0.25$ (Safety Risk: 0–100)
  - $w_4 = 0.15$ (Overdue Days: $\min(100, \text{days} \times 12.5)$)
  - $w_5 = 0.10$ (Corridor Traffic Criticality: 0–100)
- **Priority Bands:**
  - $\ge 80$: CRITICAL
  - $\ge 60$: HIGH
  - $\ge 40$: MEDIUM
  - $< 40$: ROUTINE
- **Contributor Breakdown:** Computed and returned transparently alongside every score. (No black-box ML on critical path).

### 2.2 CP-SAT Constraint Optimization Formulation
- **Decision Variables:**
  - $x_{i,j} \in \{0, 1\}$: 1 if task $i$ is assigned to block $j$.
  - $\text{is\_scheduled}_i = \sum_j x_{i,j} \in \{0, 1\}$.
  - $\text{block\_used}_j \in \{0, 1\}$: 1 if at least one task is assigned to block $j$.
  - $\text{dept\_active}_{d,j} \in \{0, 1\}$: 1 if department $d$ has $\ge 1$ task in block $j$.
- **Hard Constraints:**
  1. $\sum_j x_{i,j} \le 1, \quad \forall i$ (Each task assigned at most once).
  2. $\sum_i x_{i,j} \cdot \text{crew}_i \le \text{ResourceCapacity}_j, \quad \forall j$.
  3. $\sum_i x_{i,j} \le \text{AvailableSlots}_j, \quad \forall j$.
  4. Precedence: For task $B$ depending on $A$: $\text{is\_scheduled}_B \le \text{is\_scheduled}_A$ and $x_{A, j_A} + x_{B, j_B} \le 1$ for all block pairs where $\text{start}(j_B) < \text{end}(j_A)$.
  5. Operational Train Conflicts: Hard forbidden blocks pruned during candidate generation for Priority-1 trains (Vande Bharat, Rajdhani).
  6. Department & Safety Permissions: Hard checked in candidate opportunity model.
- **Soft Objective (Maximization):**
  - $+ 10 \times \sum_{i,j} \text{PriorityScore}_i \cdot x_{i,j}$
  - $+ 500 \times \sum_{i \in \text{Critical}} \text{is\_scheduled}_i$
  - $- 800 \times \sum_{i \in \text{Critical}} (1 - \text{is\_scheduled}_i)$
  - $+ 350 \times \sum_j \max(0, \sum_d \text{dept\_active}_{d,j} - 1)$ (Cross-Department Clubbing Bonus)
  - $- 40 \times \sum_j \text{DurationHours}_j \cdot \text{block\_used}_j$
  - $- 1.5 \times \sum_j \text{TrainDisruptionPenalty}_j \cdot \text{block\_used}_j$
  - $- 10 \times \sum_j \text{GoodsDisruptionCost}_j \cdot \text{block\_used}_j$

### 2.3 Simulated Asset Availability Proxy Formula
- Transparently labeled as a simulation proxy:
  $$\text{Simulated Asset Availability} = 80.0\% + 12.0\% \cdot \left(\frac{\text{Critical Tasks Completed}}{\text{Total Critical Tasks}}\right) + 5.0\% \cdot \left(\frac{\text{Completed Priority Score}}{\text{Total Priority Score}}\right) - 2.5\% \cdot (\text{Unscheduled Critical Tasks}) - 0.5\% \cdot (\text{Train Conflicts})$$
  Clamped between $45.0\%$ and $99.9\%$.

---

## 3. Data Architecture Boundaries

- All inputs and outputs pass through strictly typed Pydantic models.
- Adapters (`TMSAdapter`, `SMMSAdapter`, `TDMSAdapter`, `COAAdapter`) define clean future-proof interfaces.
- The UI visibly displays the persistent badge **"Synthetic / Demo Data"** to maintain architectural honesty.

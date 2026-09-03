# IBPS MODEL ASSUMPTIONS & ARCHITECTURAL BOUNDARIES

**Problem Statement 26027:** "AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways"  
**System:** IBPS (Integrated Block Planning System)  
**Mandatory Label:** `SYNTHETIC / DEMO DATA ONLY — ARCHITECTURAL PROTOTYPE`

---

## 1. Boundary Taxonomy

To ensure complete architectural integrity and honesty during Smart India Hackathon evaluations, all components in IBPS are strictly categorized into three boundaries:

```
+-------------------------------------------------------------------------+
|                        IBPS ARCHITECTURAL BOUNDARIES                    |
+-------------------------------------------------------------------------+
|  1. REAL / SOURCE-DERIVED   | Problem statement requirements,           |
|                             | departmental workflows, TMS/SMMS/TDMS/COA |
|                             | interface concepts, safety protocols.     |
+-----------------------------+-------------------------------------------+
|  2. SYNTHETIC               | Task records, track defects, timetabled   |
|                             | train movements, freight forecasts,       |
|                             | block window capacities, proxy scores.    |
+-----------------------------+-------------------------------------------+
|  3. SIMULATED               | Live CP-SAT constraint optimization,      |
|                             | emergency defect injection, dynamic       |
|                             | re-planning diffs, availability proxy.    |
+-------------------------------------------------------------------------+
```

---

## 2. Detailed Category Breakdown

### 2.1 REAL / SOURCE-DERIVED (From SIH Problem Statement 26027 & IR Procedures)
- **Departmental Roles:**
  - **Engineering (Track/Civil):** Rail fracture repair, turnout tamping, deep ballast screening, switch expansion joint adjustments.
  - **Signal & Telecommunication (S&T):** Point machine overhaul, digital axle counter (DAC) calibration, LED signal aspect maintenance, track circuit testing.
  - **Traction Distribution (TRD):** OHE contact wire stagger adjustments, bracket insulator replacements, 25kV power block isolation, auto-tensioning device (ATD) checks.
- **Legacy System Concepts:**
  - `TMS` (Track Management System)
  - `SMMS` (Signalling Maintenance Management System)
  - `TDMS` (Traction Distribution Management System)
  - `COA` (Control Office Application)
- **Safety & Operational Rules:**
  - Power block de-energization must precede track work under live OHE.
  - Premium train movements (e.g. Vande Bharat / Rajdhani) forbid disruptive heavy track possessions.
  - Mutually conflicting spatial work on the same kilometer cannot execute concurrently.
  - Human-in-the-Loop decision support rule: Final execution and block grant authority always remains with authorized railway Section Controllers / Block Planners.

---

### 2.2 SYNTHETIC (Explicitly Generated for Prototype Demonstration)
- **Maintenance Task Backlog:** 21 hand-crafted deterministic tasks (and 200 scaled synthetic records) with representative Indian Railways defect nomenclature.
- **Timetabled Train Movements:** Synthetic schedules on key trunk routes (CSTM–KYN, KYN–PUN, NDLS–GZB) with realistic priority classes.
- **Freight Traffic Forecasts:** Time-windowed freight density estimates modeling freight traffic uncertainty.
- **Corridor Block Windows:** Candidate possession slots representing shadow night blocks and midday maintenance windows.
- **Crew and Equipment Capacities:** Discrete integers modeling gang size, tower wagon availability, and BCM machine slots.

> [!IMPORTANT]
> **No Confidential Data Claim:** IBPS does not connect to internal CRIS servers or use confidential Indian Railways operational databases. All data is generated behind clean adapter interfaces (`SyntheticTMSAdapter`, `SyntheticSMMSAdapter`, `SyntheticTDMSAdapter`, `SyntheticCOAAdapter`).

---

### 2.3 SIMULATED (Computational Models)
- **Explainable Multi-Factor Priority Engine:** Deterministic formula balancing Severity, Asset Criticality, Safety Risk, Overdue Days, and Traffic Criticality without black-box ML.
- **Constraint Optimization (CP-SAT):** Genuine mathematical formulation in Google OR-Tools finding optimal allocations without hardcoded schedules.
- **Simulated Asset Availability Proxy:**
  $$\text{Simulated Asset Availability} = 80.0\% + 12.0\% \left(\frac{\text{Critical Completed}}{\text{Total Critical}}\right) + 5.0\% \left(\frac{\text{Completed Priority}}{\text{Total Priority}}\right) - 2.5\% (\text{Unscheduled Critical}) - 0.5\% (\text{Train Conflicts})$$
  *(Transparent proxy modeling asset readiness; not an official CRIS metric).*
- **What-If Emergency Re-planning:** Dynamic re-solve with soft pinning to demonstrate real-time schedule adaptation with minimal churn.

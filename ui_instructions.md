# ui_instructions.md
## IBPS — Integrated Block Planning System — Frontend Redesign Specification
### For implementation by Codex. Read this entire document before making changes.

This document is a diagnosis of the CURRENT UI (six screenshots reviewed: Overview, Planning,
Maintenance Tasks, Block Windows, What-If Replanning, Diagnostics) followed by a concrete,
numeric implementation spec. Preserve all existing functionality, routing, and API integration.
This is a visual/structural redesign, not a rewrite.

---

## 0. Product framing (do not lose this while implementing)

IBPS is an internal decision-support tool for railway maintenance planners. It is not a product
being sold to anyone. Every visual decision should be justifiable by "does this help a planner
understand the state of the corridor faster and more accurately" — never "does this look
polished." Institutional restraint beats visual flourish everywhere in this spec.

Positioning line to keep in mind: *"IBPS provides AI-assisted decision support. Final approval
and override remain with authorized railway personnel."* Nothing in the UI should look
autonomous or celebratory about automation — it should look like an instrument panel.

---

## 1. Cross-cutting findings (apply to every page)

### 1.1 — P0: Raw backend values are shown verbatim to users
**Current problem:** Diagnostics' "Unscheduled Task Diagnostics" shows
`COMPETED_OUT_BY_HIGHER_PRIORITY_TASKS (Feasible blocks: BLK-CK-NIGHT-01, BLK-CK-NIGHT-02)`.
What-If's "Defect Type" field is pre-filled with `SUDDEN_TRANSVERSE_RAIL_CRACK`. Candidate
pruning reasons elsewhere use `TRAIN_CONFLICT`, `CORRIDOR_MISMATCH`, etc. as display labels.
**Why it looks bad:** Enum constants are implementation detail. Showing them verbatim signals
the UI layer was never actually written — it's just printing whatever the API returned.
**Desired change:** Every enum-like string gets a humanization mapping at the presentation
layer (a single lookup table/function, not per-page ad hoc strings).
**Implementation:**
- Create `frontend/src/lib/labels.ts` exporting `humanizeReason(code: string): string` and
  `humanizePruneReason(code: string): string`.
- Mappings, e.g.:
  - `TRAIN_CONFLICT` → "Conflicts with a scheduled train movement"
  - `CORRIDOR_MISMATCH` → "Corridor does not match"
  - `DEPARTMENT_NOT_PERMITTED` → "Department not permitted on this block"
  - `SAFETY_CONSTRAINT_MISSING` → "Safety constraint not satisfied"
  - `DURATION_EXCEEDED` → "Task duration exceeds block window"
  - `COMPETED_OUT_BY_HIGHER_PRIORITY_TASKS` → "Displaced by higher-priority tasks competing
    for the same block(s)"
- For "Unscheduled Task Diagnostics" cards, restructure the sentence as prose:
  `"Not scheduled — displaced by higher-priority work competing for the same corridor
  blocks (BLK-CK-NIGHT-01, BLK-CK-NIGHT-02)."` Bold the block IDs only.
- For the What-If "Defect Type" field: replace the free-text input with a `<select>` of known
  defect types (sourced from whatever enum the backend already validates against). If the
  backend genuinely accepts arbitrary strings, keep free text but clear the placeholder value
  (no defect type should be pre-filled) and use sentence case placeholder text:
  `"e.g. Transverse rail crack"`.
- Any field that mirrors an internal payload key (e.g. `CRITICALITY: 100` as a bare number) gets
  a label rewrite: `"Criticality (0–100)"` with a helper caption, or converted to a slider with
  labeled bands (Routine / Medium / High / Critical) if the backend accepts a 0–100 int — a
  slider communicates the scale instantly where a bare textbox does not.

### 1.2 — P0: Duplicated content across pages
**Current problem:** The "Baseline vs IBPS" 7-metric bar chart appears, pixel-for-pixel
identical, on both Overview and Planning. The full "Objective Terms" breakdown (8 rows,
identical numbers) appears on both Planning and Diagnostics.
**Why it looks bad:** Judges and users will notice the same chart twice in one session. It
reads as unplanned information architecture rather than one coherent app with distinct pages
each answering a distinct question.
**Desired change:** Give each page ONE job.
- **Overview**: keep a compact, single-row *comparison strip* (not the full 7-metric bar
  chart) — see §4.3. Remove the full bar chart from Overview entirely.
- **Planning**: owns the full Baseline vs IBPS bar chart AND the Objective Terms breakdown,
  since this is the page whose job is "explain what the optimizer decided and why."
- **Diagnostics**: remove the duplicated Objective Terms panel. Replace it with a link/anchor
  button: `"View full objective breakdown → Planning page"` if cross-navigation is easy, or, if
  Diagnostics genuinely needs solver-internals framing, keep only a single collapsed summary
  row (`"Objective value: 16,378 — 3 positive terms, 3 penalty terms"`) with a "Details" link
  to Planning, not the full repeated bar list.
- Diagnostics keeps "Department Coordination" (that's diagnostic-specific: it's about which
  blocks satisfied cross-department feasibility, not about the plan's headline results).

### 1.3 — P1: Terminology inconsistency (ENGINEERING vs ENG)
**Current problem:** Tasks table spells out `ENGINEERING`; Overview, Block Windows, and
Diagnostics all use `ENG`.
**Desired change:** Standardize on the three-letter codes **ENG / S&T / TRD** everywhere,
including the Tasks table. Reserve the full department name only for form labels/dropdown
option text where a first-time reader needs the expansion (e.g., a `<select>`'s options can
read `"Engineering (ENG)"`), never inside a pill/badge or table cell.

### 1.4 — P0: "Card-per-fact" pattern (the strongest AI-generated signature in this UI)
**Current problem:** Overview's "Operational Insight" section wraps each single sentence in
its own bordered box with a green circular checkmark icon. Planning wraps each individual
metric (Status, Objective, Scheduled, Unscheduled) in its own small bordered box inside an
already-bordered outer card — a box inside a box inside a box.
**Why it looks bad:** This is precisely the "every piece of information gets a rounded
container" pattern the brief asks to eliminate. It fragments reading flow and roughly triples
the visual "furniture" (borders, corners, padding) needed to convey four short facts.
**Desired change:** Replace boxed lists with a plain, structured list under ONE section
header/border. Replace nested metric mini-cards with a single **metric row/table** — label
left, value right, no individual borders (see MetricStrip / DataRow components, §11).
**Implementation:** See component definitions in §7 and §11. No page should nest a bordered
container inside another bordered container more than one level deep, ever.

### 1.5 — P1: Colour has lost semantic specificity
**Current problem:** The same green is used for: a positive KPI delta, a "SCHEDULED" status
dot, the "IBPS" series in every bar chart, and a "100%" utilization bar fill. Four different
meanings, one color.
**Desired change:** Reserve green strictly for **status-positive / healthy / scheduled**
semantics (§8, Status System). Give the "IBPS" series in comparison charts the primary accent
blue (`--accent-primary`), not green — it is a category label (which plan), not a status
judgement. Utilization bars use a *neutral fill scale* (grey → blue as it approaches 100%),
reserving amber/red only for genuinely concerning utilization (over-capacity or the specific
"HIGH traffic / high train-impact" case already flagged correctly in Block Windows' `TRAFFIC`
column).

### 1.6 — P1: Numeric alignment
**Current problem:** Table numeric columns (DURATION, CREW, TASKS, TRAIN IMPACT) and KPI
figures are left-aligned.
**Desired change:** All numeric table columns right-align, using tabular (lining) numerals.
KPI headline numbers stay left-aligned only in the compact MetricStrip layout (§9) where
label-above-value reads naturally left-aligned; but any numeric *column* inside a table (not a
standalone KPI) must be right-aligned per §9 Table rules.

---

## 2. Design tokens

### 2.1 Color tokens

| Token | Hex | Why it exists |
|---|---|---|
| `--bg-app` | `#0B1117` | Base app background. Slightly darker than surfaces so panels read as raised information, not as the void. |
| `--bg-surface` | `#111926` | Primary panel/section background (replaces most current bordered "cards"). |
| `--bg-surface-raised` | `#161F2E` | Used only for the rare genuinely elevated element — a drawer, a modal, a dropdown menu. Not for ordinary page sections. |
| `--border-default` | `#22303F` | Standard 1px hairline border between sections, table rows, panel edges. |
| `--border-strong` | `#324156` | Used sparingly: focused input outline, selected row, active nav item's left rule. |
| `--text-primary` | `#E7ECF2` | Headings, primary data values, table cell text. |
| `--text-secondary` | `#96A3B5` | Section labels, table headers, field labels, captions. |
| `--text-muted` | `#5E6C80` | Metadata, timestamps, placeholder text, disabled state. |
| `--accent-primary` | `#3B82F6` | Interactive elements: buttons, links, the "IBPS" (optimized) series in comparison charts, active nav indicator. One blue, used consistently for "this is the thing you can act on / this is our system's output." |
| `--status-success` | `#22C55E` | Scheduled / feasible / positive outcome / optimal solver status. |
| `--status-warning` | `#F5A524` | Attention needed but not failure: synthetic-data disclosure, medium-traffic blocks, near-capacity utilization. |
| `--status-danger` | `#EF4444` | Infeasible / conflict / critical priority / unscheduled critical task / high train-impact. |
| `--status-info` | `#64748B` | Neutral informational states (baseline series in comparison charts, routine priority, unscheduled-but-not-critical). |

**Rules:**
- No purple, no gradients, no neon. This palette is intentionally restrained — nine colors
  total plus three greys for background layering.
- Every use of a semantic color (success/warning/danger) must correspond to an actual
  operational judgement, never decoration. If you can't name the judgement a color represents,
  use `--text-secondary` instead.
- The comparison-chart convention going forward: **Baseline = `--status-info` (slate grey)**,
  **IBPS/Optimized = `--accent-primary` (blue)**. This replaces the current grey-vs-green
  convention (green is reserved for status, not for "which plan").

### 2.2 Typography

- Font family: **IBM Plex Sans** (fallback: `-apple-system, "Segoe UI", Roboto, sans-serif`).
  Rationale: has a genuine "technical/institutional" character (used in engineering and
  transit-adjacent contexts) without reading as a trendy startup font like Inter or a rounded
  consumer font like Poppins.
- Numeric font: **IBM Plex Mono** for all table numeric columns, KPI headline values, and
  objective-term values. Use `font-variant-numeric: tabular-nums` at minimum if Plex Mono isn't
  adopted everywhere — but prefer the monospace family for anything that is a *quantity a
  planner compares row-to-row* (durations, crew counts, block hours, objective terms, solver
  wall time).

| Role | Size | Weight | Line height | Notes |
|---|---|---|---|---|
| Page title (e.g. "Tasks") | 22px | 600 | 28px | Currently ~40px — reduce. This is a workstation, not a landing page. |
| Eyebrow/kicker (e.g. "MAINTENANCE WORKBANK") | 11px | 600, uppercase, tracking +0.06em | 14px | Keep as-is, this pattern works. |
| Section header (e.g. "TASK REGISTER") | 12px | 600, uppercase, tracking +0.04em | 16px | Reduce from current ~14–16px; should be visibly quieter than page title. |
| Section subtitle/caption | 12.5px | 400 | 18px | `--text-secondary`. |
| Body / table cell | 13px | 400 | 18px | `--text-primary`. |
| Table header | 11px | 600, uppercase, tracking +0.03em | 16px | `--text-secondary`. |
| KPI headline value | 26px | 600 | 30px | Reduced from current ~32–34px. Use Plex Mono, tabular. |
| KPI label | 10.5px | 600, uppercase, tracking +0.05em | 14px | `--text-secondary`. |
| Metadata (timestamps, IDs) | 11.5px | 400 | 16px | `--text-muted`, Plex Mono for IDs like `TASK-ENG-001`. |
| Button label | 13px | 600 | — | No uppercase. |

**Numeric typography rule:** every table column containing a quantity (duration, crew, tasks,
train impact, block hours, objective values, percentages) uses Plex Mono / tabular numerals,
right-aligned, with units as a lighter-weight suffix (e.g. `150 min` where `150` is
`--text-primary` weight 500 and `min` is `--text-muted` weight 400).

### 2.3 Spacing scale (8px rhythm)

`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64` — no other spacing values permitted anywhere in the
codebase. Specifically:
- Page padding (outer margin around content): `24px` at 1280px width, `32px` at ≥1440px.
- Section-to-section vertical gap: `24px`.
- Component internal gap (e.g. label to value, icon to text): `8px`.
- Table row vertical padding: `12px` top/bottom (current rows read taller than this due to
  two-line "Activity/Defect" cells — keep two-line cells but tighten the container padding).
- Panel/section internal padding: `16px` (reduced from current ~20–24px on bordered boxes).
- Drawer padding: `24px`.
- Gap between filter controls in a filter bar: `12px`.
- Gap between KPI items in a MetricStrip: `0px` internal — separated by a `1px` vertical
  `--border-default` rule instead of gap+individual container (see §9.1).

### 2.4 Radius

- Standard corner radius: **6px** for buttons, inputs, table containers, chart containers.
- **4px** for small elements: badges/tags, small pill status indicators.
- **0px** — no radius — for: table cells, drawer panels, the outermost page-level container.
- Eliminate the current large radius (~12–16px) used on KPI cards and insight boxes entirely.
  Nothing in an operational instrument panel should look like a rounded consumer app tile.

### 2.5 Shadow

- Default: **no shadow** on any section/panel. Sections are differentiated by
  `--bg-surface` against `--bg-app` and a `1px --border-default` outline — never by elevation.
- The ONLY places a shadow is permitted: an open dropdown menu, an open drawer's overlay edge,
  a toast/notification. Shadow value in those cases: `0 4px 16px rgba(0,0,0,0.4)`, nothing more
  dramatic.

### 2.6 Layout / grid

- Desktop-first. Target breakpoints: 1280px (minimum supported), 1440px (primary design
  target), 1920px (should gain content width, not just margin).
- Sidebar width: **236px** fixed, non-collapsible for the prototype (collapsing is a P3, not
  needed for a hackathon demo — don't build it unless time remains).
- Max content width: none — at 1920px, content should use the extra width for wider tables and
  a 3rd chart column where relevant, not just add horizontal whitespace on the sides. This is
  an operations tool; horizontal density is a feature.
- Content grid: 12-column, `24px` gutter, page padding per §2.3.
- Standard two-column page split (used on Planning, What-If): **50/50** or **60/40** — never
  an awkward 70/30 that leaves one side visually starved.

---

## 3. Cards — when to use one, and when not to

**Rule:** A bordered container ("card") is justified only when it groups genuinely
heterogeneous content that needs a visual boundary to avoid bleeding into an adjacent,
unrelated section. It is NOT justified for:
- A single metric (label + value + delta) — use MetricStrip (§9.1), not one card per metric.
- A single sentence or bullet point — use a plain list under one section header.
- A single form field — forms use flat sections with rules between field groups, not per-field
  boxes.

**When a section-level container (not "card" — call it a Panel) IS appropriate:**
- A table plus its header/filter row (one panel: header, controls, table).
- A timeline/Gantt visualization.
- A chart plus its title/caption.
- A drawer.

**Panel spec:** `--bg-surface` background, `1px solid --border-default`, `6px` radius, `16px`
padding, no shadow. A panel has exactly one header row (eyebrow + title + optional caption)
before its content — do not nest a second bordered box for the header inside the panel.

**Specific fixes required:**
- Overview "Operational Insight": ONE panel, header "OPERATIONAL INSIGHT", then a plain list
  (small `--status-success` checkmark glyph inline before each line, not a boxed icon), lines
  separated by `1px --border-default` hairlines, not individual boxes.
- Planning's Status/Objective/Scheduled/Unscheduled 2×2 grid: replace the 4 nested mini-boxes
  with a single 4-column MetricStrip row (§9.1) inside the existing Baseline/IBPS panel — no
  inner borders at all.
- Diagnostics' top 4 metrics (Optimization Status, Hard Constraints, Candidate Pairs, Solver
  Wall Time): same treatment — one MetricStrip row, not 4 separate bordered boxes.

---

## 4. Top bar

- Height: **56px**.
- Left: breadcrumb-style eyebrow + page title (already present pattern — keep, but shrink per
  §2.2 typography).
- Right, in this fixed order: (1) dataset indicator (`Dataset: demo_fixture`, plain text,
  `--text-muted`, not a boxed badge), (2) Synthetic/Demo data indicator — see §4.1, (3) backend
  connection status — see §4.2.
- No greeting copy of any kind ("Good morning", "Welcome back") — this bar states system facts,
  never addresses the user socially.

### 4.1 — Synthetic/Demo data indicator
**Current:** a loud orange filled pill, `"SYNTHETIC / DEMO DATA ONLY — ARCHITECTURAL
PROTOTYPE"`, competing visually with the actual page title next to it.
**Change:** Keep this disclosure *always visible* (correct instinct, don't remove it), but
demote its visual weight so it reads as a persistent system fact, not an alert. Use a small
outline-style tag (not filled): `1px solid --status-warning`, text `--status-warning`,
background transparent, `4px` radius, text: `"SYNTHETIC DATA"` (drop "ONLY — ARCHITECTURAL
PROTOTYPE" — that phrase belongs in the sidebar footer caption where it already correctly
appears: "Decision-support prototype. Not connected to live Indian Railways systems.").

### 4.2 — Backend status
Keep the green-dot + "Backend ok" pattern — this is a correct, minimal use of a status
indicator. No changes needed beyond making the dot 8px and using `--status-success`.

---

## 5. Sidebar

- Width `236px`, background `--bg-app` (one shade darker than content area — sidebar recedes,
  content advances).
- Logo block: keep "IBPS" wordmark + "Integrated Block Planning System" + "Ministry of
  Railways – Decision Support Prototype" caption exactly as-is — this is one of the few places
  in the current UI that already reads correctly institutional. Do not change size/weight here.
- **Group navigation into three labeled sections** (currently a flat list of 6 items):
  ```
  MONITOR
    Overview
  PLAN
    Planning
    Maintenance Tasks
    Block Windows
    What-If Replanning
  TECHNICAL
    Diagnostics
  ```
  Section labels: 10px, 600 weight, uppercase, `--text-muted`, `8px` bottom margin, `24px` top
  margin from previous group.
- Nav item: `40px` height, `13px` label, icon `16px` (current icon sizing looks correct —
  keep). Active state: `--border-strong` 2px left rule + `--bg-surface` background tint + label
  color `--text-primary`; inactive: `--text-secondary` label, no background.
- Icon set: keep current outline-style icon set (Lucide or equivalent) — stroke weight should
  be consistently `1.5px` across every icon in the app (verify current icons match; some may be
  mixed weight).
- Footer (System Status block): keep the two status dots pattern (API Connected, Synthetic Demo
  Data) — correct pattern, just align dot size to `8px` to match the top bar's backend dot for
  consistency, and move the descriptive caption text below it to `11px` `--text-muted`.

---

## 6. Status system

Define once, reuse everywhere via a single `<StatusTag>` component.

| Status | Color token | Treatment |
|---|---|---|
| CRITICAL | `--status-danger` | Filled badge, small, uppercase, used only in Priority column and KPI deltas that are genuinely bad. |
| HIGH | `--status-warning` | Filled badge. |
| MEDIUM | `--status-info` | Outline badge (not filled — reserve filled for the two ends of the urgency spectrum). |
| ROUTINE | `--text-muted` | Plain text, no badge at all. Not everything needs a badge — routine is the "nothing to see here" case and should recede, not compete visually with CRITICAL. |
| SCHEDULED | `--status-success` | Small dot + text, no filled pill (current dot+text pattern for status column is correct — keep it, don't "upgrade" it to a filled badge). |
| UNSCHEDULED | `--text-muted` | Dot (grey) + text. |
| FEASIBLE | `--status-success` | Text only, no badge — used in dense diagnostic contexts where a badge per row would be too heavy. |
| INFEASIBLE | `--status-danger` | Text only. |
| BLOCKED | `--status-danger` | Small dot + text, consistent with SCHEDULED/UNSCHEDULED pattern. |
| EMERGENCY | `--status-danger` | Filled badge — this is the one place a strong filled treatment is justified, since it should visually interrupt. |
| OPTIMAL / FEASIBLE (solver) | `--status-success` | Plain large text value (already correct on Planning/Diagnostics — keep as headline text, not a badge). |

**Badge vs plain text rule:** Use a filled/outline badge only in a *table column scanned
top-to-bottom for triage* (Priority column, Department column). In a *detail or summary
context* (drawer body, diagnostic sentence, KPI caption) use plain colored text — badges in
prose read as noisy.

**Department tags:** keep as small outline badges (ENG / S&T / TRD) — this is already a
reasonable, restrained use of a badge since departments are genuinely categorical and scanned
quickly across rows/blocks. Standardize the three department colors: ENG = `--accent-primary`
tint, S&T = a muted violet-grey (`#7C7FA6`, used ONLY for this one purpose, not added to the
general palette), TRD = `--status-success` tint at low opacity outline. Keep these three
consistent across every page (Overview, Tasks, Blocks, Diagnostics currently show slightly
different color assignments for the same department — audit and unify).

---

## 7. Component architecture

```
AppShell
├── Sidebar
│   ├── Brand
│   ├── NavGroup (×3: Monitor / Plan / Technical)
│   └── SystemStatusFooter
├── TopBar
│   ├── PageHeading (eyebrow + title)
│   └── SystemIndicators (dataset, synthetic tag, backend status)
└── PageContainer
    ├── PageHeader (title + subtitle, page-level)
    ├── MetricStrip (label/value/delta row, replaces individual KPI cards)
    ├── Panel (generic bordered section: header + content)
    │   ├── FilterBar (search + selects, used on Tasks)
    │   ├── DataTable (see §9)
    │   ├── Timeline (see §10, Block Windows)
    │   ├── ComparisonChart (Baseline vs IBPS bars)
    │   ├── ObjectiveTermList (labeled horizontal bars, signed values)
    │   └── InsightList (plain list with inline status glyphs, replaces boxed insight cards)
    ├── StatusTag (see §6)
    ├── DepartmentTag
    ├── Drawer (task/block detail)
    └── EmptyState / ErrorState / LoadingState
```

**Remove:** the current pattern of ad hoc bordered `<div>`s per metric (seen on Planning's
Status/Objective/Scheduled/Unscheduled grid and Diagnostics' top-4 metrics) — replace both call
sites with `MetricStrip`.
**Create:** `MetricStrip`, `StatusTag`, `DepartmentTag`, `InsightList`, `ObjectiveTermList` as
shared components — currently these appear to be hand-built per page, causing the inconsistent
treatments noted throughout this document.
**Reuse:** the existing filter bar pattern from Tasks (search + 3 selects) is well-built —
promote it to a shared `FilterBar` component so Block Windows or future pages can reuse it
rather than rebuilding.

---

## 8. Page-by-page specification

### 8.1 Overview

**What the eye currently sees first:** the 6 equally-weighted bordered KPI boxes, because they
occupy the full width immediately below the header at large size.
**What it should see first:** whether anything needs attention right now — i.e., the presence
of any CRITICAL/unscheduled item or a train conflict.

**Changes:**
1. Replace the 6-card KPI row with a single **MetricStrip** (§9.1): one panel, no individual
   borders, `1px` vertical separators between the 6 metrics. Reduce headline number size per
   §2.2. Give "Train Disruptions" a `--status-danger` value color when count > 0 (currently
   shown as neutral white text — this is the biggest missed signal on the page: a page whose
   job is "what needs attention" should visually flag its own conflict count).
2. Remove the full 7-metric "Baseline vs IBPS" bar chart from this page (duplicated with
   Planning — see §1.2). Replace with a compact **3-metric comparison strip**: Priority Score
   Fulfilled, Asset Availability, Coordinated Blocks — the three numbers a planner actually
   scans first — shown as small paired bars (baseline/IBPS) inline in the MetricStrip's caption
   row, not a separate chart.
3. Keep "Operating Summary" but tighten to a plain label/value list (no per-row card, already
   close to this — verify no stray inner borders).
4. "Highest Priority Tasks" table and "Upcoming Block Windows" list: keep side by side, this
   layout works. In the block list, hide `"train cost 0"` when the value is zero (only show
   train-cost figures when non-zero — a zero-cost line for every block is noise).
5. "Operational Insight": convert to `InsightList` per §3.

### 8.2 Planning

**What it should answer, per the brief:** "what did the optimizer decide, and is it better
than the fragmented baseline." Currently mostly does this, but buried in nested boxes.

**Changes:**
1. Top row (Planning Options / Planning Method): fine as two panels side by side — keep.
2. Baseline Plan / IBPS Optimized Plan columns: collapse the 2×2 metric grid + 4 stacked metric
   rows into ONE MetricStrip per column (8 metrics total per plan, in a single vertical list
   with label-left/value-right, `1px` row separators, no individual boxes). This removes 8
   nested bordered boxes per column, 16 total on this page currently.
3. Keep "Objective Terms" section — this is a genuinely good, technical, credible piece of the
   UI. Fix the bar-scale problem (§1.5... note in your findings the objective bars problem is
   really about scale, restated here): use a **diverging bar** anchored at a shared zero point,
   with positive terms extending right in `--accent-primary` and negative (penalty) terms
   extending left in `--status-danger`, all sharing one consistent px-per-unit scale (not
   independently normalized per row) — this makes the actual proportion between e.g. `+16378`
   and `-720` honestly visible instead of both rendering as near-full bars.
4. Keep the bottom Baseline vs IBPS bar chart HERE (this page owns it — see §1.2) but fix the
   axis problem from §1.5-general: split into 2 small multiples instead of one 7-series 0–100
   chart — Chart A: percentage-based metrics (Priority Score Fulfilled, Block Capacity
   Utilization, Asset Availability) on a shared 0–100 axis; Chart B: count-based metrics
   (Critical Safety Defects Cleared, Cross-Department Coordinated Blocks, Train
   Conflicts/Disruptions) on their own auto-scaled axis. Total Track Possession Hours Used gets
   its own single comparison bar pair since it's a different unit (hours) from both groups.
5. Rotate x-axis labels no more than 20° — current ~45–60° rotation is hard to read at a
   glance; prefer wrapping labels onto 2 lines over steep rotation.

### 8.3 Maintenance Tasks

This page is the closest to "already correct" in the current UI — it's a real, dense,
data-forward table. Preserve its structure; apply targeted fixes only.

1. Standardize department pills to `ENG / S&T / TRD` (§1.3) — currently spells out
   "ENGINEERING."
2. Right-align DURATION and CREW columns, Plex Mono, tabular numerals (§1.6, §2.2).
3. Tighten row vertical padding to `12px` (§2.3) — current rows read slightly taller than
   needed given the two-line Activity/Defect cell is the actual height driver; don't add extra
   padding on top of that.
4. Add visible row count / pagination state if the dataset can exceed one screen (`"21 task
   records returned by API"` caption already exists — good, keep it, but add page controls
   once task count exceeds ~30–40 so the table doesn't silently truncate).
5. Detail drawer (referenced in brief, not fully visible in screenshots — specify explicitly):
   width `420px`, slides from right, overlay `rgba(0,0,0,0.5)` behind it (page content stays
   visible, not replaced). Sections top-to-bottom: Identity (task ID, department tag, corridor)
   → Priority (band + numeric score + a small horizontal contributor breakdown using the same
   `ObjectiveTermList`-style bar component as Planning, for visual-language consistency) →
   Severity/Deadline/Duration/Crew as a MetricStrip → Candidate Blocks list (block ID,
   feasible/infeasible via plain `StatusTag` text treatment, and if infeasible, the humanized
   reason from §1.1) → Precedence (if any). Close via `×` top-right and via clicking the
   overlay; do not close on outside-click accidentally while a form is mid-edit elsewhere.

### 8.4 Block Windows

**Current problem, restated with implementation guidance:** the "Operational Timeline" is not
actually a timeline — it's a row of colored chips with a single date label and no way to judge
duration, gaps, or alignment across corridors.

**Required rebuild:**
1. Add a real time axis header: hour tick marks (e.g., every 3 hours across the visible window)
   with vertical gridlines running down through all corridor rows, `1px --border-default`,
   labeled in `--text-muted` 11px.
2. Block chips are positioned and WIDTH-SCALED proportionally to their actual start/end time
   against that axis — not floated arbitrarily. A 3-hour block must visibly be 3× the width of
   a 1-hour block.
3. Truncated labels (`"KP-ENG-..."` currently) get a hover tooltip showing the full block ID
   and time range; if the chip is too narrow to show any label, show only the department tag
   dot(s) and rely on the tooltip — don't truncate mid-word with no way to recover the full
   text.
4. Keep the department-tag-in-chip pattern (ENG/S&T/TRD shown inside or beside each chip) —
   this is useful information, keep it, just ensure chip color follows the *dominant department
   or a neutral scheduled-blue* rather than the current inconsistent mix of green/blue chip
   fills that don't map to a documented rule. Rule: chip fill = `--accent-primary` at reduced
   opacity for all scheduled blocks, department tags inside/below convey which departments,
   traffic level (LOW/MEDIUM/HIGH) shown as a colored left-edge stripe on the chip
   (`--status-success` / `--status-warning` / `--status-danger`) rather than chip fill color —
   this fixes the current overloading of green (§1.5) by moving the "traffic" signal to a
   distinct visual channel (edge stripe) from the "is this scheduled" signal (fill).
5. Block Register table below: keep as-is structurally (it's a solid table), apply §1.6
   right-alignment to TASKS, TRAIN IMPACT columns, and keep the inline utilization bars (good
   pattern) but recolor per §1.5 (neutral grey→blue fill scale, not orange/green).
6. Block detail drawer (specify explicitly, same shell as §8.3): Identity → Time window → Slot
   capacity vs used (a MetricStrip pair) → Departments (tags) → Assigned tasks (mini-table:
   task ID, department, duration) → Traffic/train-impact (plain labeled value, colored per
   §1.5 edge-stripe convention, not a big badge).

### 8.5 Planning What-If Replanning

1. Keep the Before → Action → After 3-panel flow header — clear, good pattern for
   communicating a workflow step, matches the brief's "simulate an operational event" framing.
2. Fix the Defect Type field per §1.1 (no pre-filled enum-looking string).
3. Rebalance layout: move the Emergency Defect Input form into a **left column at ~40% width**;
   reserve the **right 60%** permanently for a results panel with an explicit empty state
   (§8.6) reading `"Replan results will appear here after you submit an emergency defect."` —
   this fixes the current huge disproportionate dead space below the form by giving that space
   a defined job even before the user acts.
4. After replanning, the right panel becomes the **diff view** — this must be the visual
   centerpiece per the brief. Structure: a compact before/after MetricStrip (KPIs that changed,
   with visible delta), then a 3-group task list: **Newly Scheduled** (the emergency task +
   anything shifted into a freed slot), **Moved** (block reassigned), **Displaced/Unscheduled**
   (bumped by the emergency task, with the humanized reason from §1.1), **Unchanged** (collapsed
   by default — a count with a "show" toggle, since this list is usually the longest and least
   interesting).
5. CRITICALITY input: convert the raw `100` numeric field to a labeled slider (0–100) with
   band labels underneath (Routine / Medium / High / Critical) so the number's meaning is
   legible without cross-referencing the priority engine docs.

### 8.6 Diagnostics

1. Top 4 metrics → MetricStrip, not 4 boxes (§3).
2. Remove the duplicated Objective Terms panel (§1.2) — replace with the single collapsed
   summary + link as specified there.
3. Keep Candidate Analysis / Pruning Reasons side-by-side horizontal-bar panels — this is
   good, genuinely technical, appropriately dense content. Just apply the shared
   `ObjectiveTermList`-style bar component here too for visual consistency with Planning (they
   currently look like independently built bar-list widgets; unify into one reusable
   `LabeledBarList` component used by both Objective Terms, Pruning Reasons, and Candidate
   Analysis).
4. "Department Coordination" list: keep, but reconcile against §6's unified department tag
   colors.
5. "Unscheduled Task Diagnostics" cards: keep as a 3-column row of small panels (this
   granularity is appropriate here since each is a genuinely distinct diagnostic case), but
   rewrite the reason text per §1.1's humanization rule and bold only the block ID references.

---

## 9. Shared components — exact specs

### 9.1 MetricStrip
- One row, N columns (typically 4–8), inside a single Panel.
- Each column: label (10.5px, uppercase, `--text-secondary`) above value (26px, Plex Mono,
  `--text-primary`, or semantic color if the value itself represents a status judgement — e.g.
  Train Disruptions > 0 renders in `--status-danger`).
- Optional delta caption below value: 11.5px, `--text-muted`, with an inline ↑/↓/— glyph
  colored `--status-success`/`--status-danger`/`--text-muted` respectively.
- Columns separated by `1px solid --border-default` vertical rule, `24px` horizontal padding
  each side of the rule. No individual box borders around any column.

### 9.2 Tables
- Header row: `40px` height, `--bg-surface`, `--text-secondary` 11px uppercase labels, bottom
  border `1px --border-strong`.
- Body row: min `48px` height (allows the two-line Activity/Defect pattern without feeling
  cramped), bottom border `1px --border-default`, no vertical column borders (rely on spacing
  and right-alignment, not gridlines, to separate numeric columns).
- Hover: `--bg-surface-raised` background tint, no border/shadow change.
- Selected/active row (e.g. currently-open-in-drawer): left `2px --accent-primary` rule.
- Numeric columns: right-aligned, Plex Mono, tabular numerals (§1.6).
- Sticky header on scroll for any table likely to exceed one screen (Tasks register, Block
  register).
- Sorting: click header to sort, small chevron glyph appears on the active sort column only —
  don't show sort chevrons on every column by default (visual noise).

### 9.3 Buttons
| Variant | Height | Radius | Fill | Border | Text |
|---|---|---|---|---|---|
| Primary | 36px | 6px | `--accent-primary` | none | white, 13px 600 |
| Secondary | 36px | 6px | transparent | `1px --border-strong` | `--text-primary` |
| Tertiary/link | 36px | 0 | transparent | none | `--accent-primary` |
| Danger | 36px | 6px | `--status-danger` | none | white |
| Icon button | 32×32px | 6px | transparent, `--bg-surface-raised` on hover | none | icon only |

No button should be full-width unless it is the sole action in a narrow form column (the
current "Generate Optimized Plan" and "Inject Emergency Defect and Replan" buttons are
appropriately sized already — keep their width-to-content sizing, just confirm 36px height and
6px radius per this table, down from their current larger rounded appearance).

### 9.4 Charts
- No 3D, no donuts, no gradients, no per-bar rounded-top corners (currently bars appear to have
  slightly rounded tops — flatten to 2px radius max, top-only, to stay quiet).
- Grid lines: `--border-default`, horizontal only, no vertical gridlines behind bar charts.
- Two-series comparison bars: Baseline = `--status-info`, Optimized/IBPS = `--accent-primary`
  (§2.1) — replaces current grey/green.
- Axis labels: `--text-muted`, 11px, rotate ≤20° or wrap to two lines instead of steep angles.

---

## 10. Loading / empty / error states

Never use "Oops!" or exclamation-mark copy. Pattern:

```
[Icon: muted, 24px, no color]
<Primary line, 14px, --text-primary>: e.g. "Unable to load block plan."
<Secondary line, 13px, --text-muted>: e.g. "The planning service did not respond."
[Secondary button: Retry]
```

Empty states (e.g. What-If before submission, or a filter returning zero tasks) use the same
shell without the retry button:
```
<Primary line>: "No tasks match the current filters."
<Secondary line>: "Adjust the department, priority, or corridor filter to see results."
```

---

## 11. Micro-interactions

Permitted: drawer slide-in (200ms ease-out), row hover background fade (120ms), button
active-state (instant, no transition needed beyond a slight background darken), skeleton
loading shimmer for tables while data loads. Not permitted: bounce, floating/parallax cards,
animated gradients, count-up number animations on KPI values (they should just render the final
value — an animated tick-up on a railway ops dashboard is decorative, not informative).

---

## 12. Accessibility

- All status information (StatusTag, department tags, traffic stripes) must be distinguishable
  without color alone — pair every color-coded status with a text label or a distinct
  glyph/dot, never color-only (this is already mostly true — verify the Block Windows traffic
  stripe change in §8.4 keeps a text label "LOW/MEDIUM/HIGH" alongside the stripe, not stripe
  alone).
- Contrast: `--text-primary` on `--bg-surface` must meet 4.5:1 minimum — verify after any color
  token tuning.
- All interactive elements (table rows that open drawers, filter selects, buttons) must be
  keyboard-reachable and show a visible focus ring using `--border-strong` at 2px.
- Tables use proper `<table>` semantics (`<th scope="col">`, etc.), not div-grids styled to
  look like tables — needed for screen-reader users to navigate row/column context.

---

## 13. "Vibe-coded UI" checklist — verify before calling this done

- [ ] No metric is wrapped in its own individually-bordered card (MetricStrip used everywhere).
- [ ] No single sentence/bullet is individually boxed (InsightList used, not card-per-line).
- [ ] No duplicated chart or data panel appears on two different pages.
- [ ] No raw enum/constant string (`ALL_CAPS_WITH_UNDERSCORES`) is visible anywhere in the
      rendered UI — audit every page for this specifically.
- [ ] Department abbreviations are consistent (ENG/S&T/TRD) on every page including Tasks.
- [ ] Green is used only for status-positive/scheduled meaning, never simultaneously as a
      chart-series label for "IBPS."
- [ ] No bar chart mixes percentage-scale and count-scale metrics on one shared axis.
- [ ] The Block Windows timeline has visible time-axis gridlines and width-scaled chips.
- [ ] No card/panel corner radius exceeds 6px anywhere in the app.
- [ ] No shadow appears on any static (non-overlay) panel.
- [ ] All table numeric columns are right-aligned with tabular numerals.
- [ ] No page has more than one level of nested bordered containers.
- [ ] No greeting/social copy ("Good morning", "Welcome back") anywhere in the top bar.
- [ ] Every semantic color use maps to a documented operational judgement, listed in §6/§2.1 —
      no color used purely for visual variety.

---

## 14. Implementation priority

**P0 (must fix — currently makes the product look unfinished/AI-generated):**
- §1.1 Enum/raw-string leakage into UI text
- §1.2 Duplicated charts/panels across pages
- §1.4 Card-per-fact pattern (MetricStrip, InsightList rollout)
- §8.4 Block Windows fake timeline → real time-scaled timeline

**P1 (strongly recommended — credibility and consistency):**
- §1.3 Department terminology consistency
- §1.5 Color semantic overload (green overuse, chart series colors)
- §1.6 Numeric alignment / tabular numerals
- §8.2 Objective Terms diverging-scale bar fix
- §8.5 What-If layout rebalance + diff-view centerpiece

**P2 (polish):**
- §2.2 Typography scale reduction (page titles, KPI numbers)
- §9.4 Chart bar corner radius / gridline cleanup
- §5 Sidebar nav grouping into Monitor/Plan/Technical
- §10 Empty/error state copy standardization

**P3 (optional, only if time remains):**
- Sidebar collapse behavior
- Table pagination beyond current dataset size
- Count-up/skeleton loading polish beyond basic shimmer

---

## 15. Final design philosophy — keep these in mind while implementing

1. **Every box must earn its border.** If removing a container's border and background would
   lose no information, remove it.
2. **Color is a judgement, not a decoration.** If you can't say which operational fact a color
   represents, use grey.
3. **A planner should never see a word the backend uses internally.** Every enum, every code,
   every status constant gets translated into a sentence a human wrote.
4. **Density is not the enemy here — inconsistency is.** This is a control-room tool for people
   who will use it daily; favor a dense, scannable table over a sparse, spaced-out card grid,
   but keep that density's rules (alignment, spacing scale, row heights) rigorously consistent.
5. **Nothing should look like it's celebrating the AI.** No congratulatory tone, no "optimized!"
   flourish — the CP-SAT result is presented the way a signal engineer would read an interlocking
   diagram: plainly, and with the reasoning available on demand, not on display by default.
6. **IBPS should look like software railway engineers could actually use** — not a hackathon
   dashboard trying to look like software railway engineers could use. The difference is in the
   restraint of every choice in this document, applied consistently, everywhere, all the time.

# MASTER PROMPT — IBPS Swiss/International Typographic Restyle
### For Antigravity. Copy everything below into the prompt box.

---

## ROLE

You are restyling the existing IBPS (Integrated Block Planning System) frontend. The backend,
routing, data flow, and existing component architecture (MetricStrip, StatusTag, DepartmentTag,
LabeledBarList, InsightList, DataTable, Timeline, Drawer) already work and must not be rebuilt
from scratch. This is a **visual and structural styling pass**, not a feature change. Do not
touch backend logic, API contracts, or business logic. Do not remove functionality.

The current UI is dark-navy, rounded-corner, bordered-card, badge-heavy — a competent but
generic "AI SaaS dashboard" look. Your job is to replace that visual language entirely with a
**strict Swiss / International Typographic Style** treatment: the design lineage of Josef
Müller-Brockmann, Massimo Vignelli, and — most relevant here — **Swiss Federal Railways (SBB)**,
whose timetable boards, station signage, and the SBB clock are the canonical reference for
railway information design in exactly this style. IBPS is railway software; it should look like
it was designed by the same tradition that designed railway information systems.

---

## 0. Reference points (study these mentally before styling anything)

- **SBB (Swiss Federal Railways) timetable and signage system** — black type on white/pale
  background, a single red accent used only functionally (departures, alerts), grid-locked
  numerals, Frutiger/Helvetica-family type, zero ornamentation. This is the single closest
  real-world analogue to what IBPS should look like, and it is literally a railway system —
  use this as the north star.
- **Josef Müller-Brockmann poster grids** — rigid modular grids, asymmetric placement of large
  type against small type, generous structural whitespace (not decorative whitespace — space
  that is itself part of the grid).
- **Massimo Vignelli's NYC Subway map / Vignelli Canon** — restrained palette, one weight of
  sans-serif doing all the work, information hierarchy created by size and position, never by
  color variety or containers.

None of these use dark backgrounds, rounded corners, drop shadows, gradients, or card-per-fact
patterns. Internalize that this is not a "dark theme cleaned up" — it is a different visual
system built on light backgrounds, hairline rules, and typographic scale contrast instead of
color, borders, and boxes.

---

## 1. Non-negotiable constraints

1. **Light background as the primary theme.** Base background is near-white
   (`--bg-app: #FAFAF8`), not navy. If a dark mode is wanted later, it is a secondary toggle
   built after the light theme is correct — do not default to dark.
2. **Zero corner radius, anywhere.** Every rectangle — buttons, inputs, table containers,
   status tags, chart bars, timeline blocks — has `border-radius: 0`. No exceptions.
3. **Zero drop shadows, anywhere.** Depth and separation come only from rule lines (hairline
   borders) and whitespace, never from elevation.
4. **One accent color, used only functionally.** Red (`--accent: #D5001C`, the SBB/Swiss-flag
   red family) is reserved exclusively for: critical priority, alerts/conflicts, the single
   most important number on a page. It must never be decorative. Everything else is black,
   white, and a restrained grey scale.
5. **Replace every "card"/bordered-box with a grid position + rule lines.** If the current
   component is a bordered rounded panel, the Swiss equivalent is: content placed in its grid
   cell, separated from neighboring content by a `1px` black or grey hairline (horizontal
   and/or vertical), with no enclosing box.
6. **Typographic scale does the hierarchy work that color/boxes currently do.** A number that
   matters is large — very large, disproportionately large relative to its label — not boxed
   and not colored. Reserve red exclusively for genuine alerts, not for "important."
7. **Flush-left, ragged-right, always.** No centered text, no centered layouts, anywhere in the
   app.
8. **Preserve every existing data field, table column, filter, drawer section, and page.** This
   is restyling, not re-scoping.

---

## 2. Color tokens

| Token | Value | Use |
|---|---|---|
| `--bg-app` | `#FAFAF8` | Page background — a very slight warm off-white, not pure clinical `#FFFFFF`, not grey. |
| `--bg-inverse` | `#0A0A0A` | Used only for isolated high-contrast blocks — e.g. a single KPI panel that is deliberately inverted (black background, white type) as a Swiss-poster-style accent moment. Use sparingly — at most one inverted block per page. |
| `--ink` | `#111111` | Primary text/type, near-black not pure black (matches classic Swiss print, which was never 100% black). |
| `--ink-secondary` | `#5A5A5A` | Labels, captions, secondary data. |
| `--ink-muted` | `#9A9A9A` | Metadata, placeholder, disabled. |
| `--rule-default` | `#D9D7D2` | Standard hairline rule between sections/rows. |
| `--rule-strong` | `#111111` | Heavier rule for major section breaks (e.g. under a table header, under a page title) — full black, not grey. |
| `--accent` | `#D5001C` | The ONE accent. Critical status, alerts, train conflicts, the single most important figure on a page. |
| `--accent-tint` | `#F6D9DC` | Extremely restrained use only as a background wash directly behind an accent numeral if legibility requires it — not for general "highlighting." |

No blue, no green, no orange, no purple anywhere. This is a deliberate reduction from the
previous 9-color operational palette. Status meaning that used to be color-coded (scheduled,
feasible, high, medium, routine) is now carried by **typographic weight, size, and position**,
with red reserved solely for critical/conflict. Example: "SCHEDULED" is plain `--ink` text at
normal weight; "UNSCHEDULED" is `--ink-muted`; "CRITICAL" is `--accent` red, bold, and larger
than surrounding text — not a filled pill in any case.

---

## 3. Typography

- **Single family: a grotesque sans.** Use `Helvetica Neue` with fallback
  `"Neue Haas Grotesk", Arial, sans-serif`. If a licensed grotesque isn't available, `Inter` is
  an acceptable substitute but must be used at normal (not rounded) optical settings.
  Do NOT use a "tech" typeface (no Space Grotesk, no geometric rounded sans) — grotesques only.
- **Numerals: monospace/tabular for data tables only** (keep IBM Plex Mono or similar for table
  columns and objective-term values — Swiss timetables also use strongly gridded numerals for
  exactly this reason). Headline KPI figures use the grotesque sans at very large scale, not
  monospace — a huge "94.1" in Helvetica-family, not in a mono font, is the correct
  timetable-board convention (compare: SBB departure boards use grotesque, not mono).
- **Extreme scale contrast is the point.** Define a small, deliberately non-linear scale:

| Role | Size | Weight | Notes |
|---|---|---|---|
| Hero figure (the one number on Overview that matters most) | 96–120px | 700 | Used at most once per page. This replaces the old uniform KPI-card grid — one number gets to be enormous; the rest are much smaller. |
| Page title | 40px | 700 | Set flush-left at a grid column boundary, never centered, often overlapping/breaking the grid slightly per classic Müller-Brockmann asymmetry (e.g. title starts at column 1 but a related number sits large at column 9). |
| Section label (eyebrow) | 11px | 600, uppercase, tracked +0.08em | Keep uppercase tracking — this is one of the few things the current UI already does in a Swiss-compatible way. |
| Secondary KPI figure | 28–32px | 700 | For KPIs that matter but aren't THE hero figure of the page. |
| Body / table cell | 13px | 400 | `--ink`. |
| Table header | 11px | 600, uppercase, tracked +0.04em | `--ink-secondary`, sits directly above a `2px --rule-strong` line (not a soft grey border). |
| Caption/metadata | 11px | 400 | `--ink-muted`. |

- No size between these should be invented ad hoc — five or six defined sizes total, used with
  large jumps between them, not a smooth continuous scale. The jump itself (96px next to 13px
  on the same page) is what reads as "Swiss," not any individual size.

---

## 4. Grid system

- **12-column grid**, `24px` gutters, page margins `48px` at desktop widths (≥1440px), `32px`
  at 1280px.
- The grid is **visible in structure even when not drawn** — every panel, every KPI, every table
  aligns to a column boundary. No floating/arbitrary positioning.
- **Deliberate asymmetry is required, not optional.** Do not center content within its column
  span. Do not make every section the same width. Examples:
  - Overview: hero figure occupies columns 1–5 at 96px; a secondary metric cluster occupies
    columns 7–12 at normal KPI scale — an intentionally uneven split, not a uniform 4-up or
    6-up grid of equal boxes (which is exactly the "SaaS KPI card row" pattern being eliminated).
  - Planning: Baseline panel might occupy columns 1–5, an intentionally wider IBPS Optimized
    panel occupies columns 6–12 (since it is the more important of the two) — asymmetric widths
    encode importance, replacing the old equal-width two-column card layout.
- Rule lines (`1px --rule-default`, `2px --rule-strong` for major breaks) replace panel borders
  as the way columns/sections are separated. A page can and should have visible vertical rule
  lines between major grid regions — this is correct Swiss grid practice, not a container border.

---

## 5. Component re-expression

### 5.1 Status (replaces StatusTag pill component)
No filled rounded pills. New treatment:
- **CRITICAL**: text set in `--accent`, weight 700, same size as surrounding text but bold —
  optionally preceded by a solid `8×8px` red square (no radius) as a glyph, not a pill.
- **HIGH**: `--ink`, weight 700 (bold black, not colored — reserve the accent strictly for
  CRITICAL/conflict, per constraint #4).
- **MEDIUM / ROUTINE**: `--ink-secondary` / `--ink-muted`, weight 400. Routine essentially
  recedes to near-invisible, exactly as it should — the eye should never be drawn to routine.
- **SCHEDULED / UNSCHEDULED**: plain text, no dot, no badge — `--ink` for scheduled,
  `--ink-muted` for unscheduled. If a glyph is wanted, use a small filled or outline square,
  never a circle-dot-plus-pill combination.

### 5.2 Department tags
Replace colored rounded pills (ENG/S&T/TRD) with **bracketed text**: `[ENG]` `[S&T]` `[TRD]` set
in the table's normal type weight, `--ink-secondary`, square brackets literally rendered as part
of the label — a direct timetable-board convention (compare platform indicators on European
departure boards). No fill color per department at all; the bracket notation alone provides
enough scanability at this data density.

### 5.3 MetricStrip → asymmetric figure blocks
Do not keep the "row of equal-width metrics separated by a vertical rule" pattern verbatim.
Instead:
- One metric per page is the **hero figure** (§3), placed large, alone, with its label small
  and directly beneath it, left-aligned.
- Remaining metrics are shown in a **tight tabular list**: label flush-left, value flush-right,
  set in the secondary-KPI size, each row separated by a `1px --rule-default` hairline — this
  is much closer to a timetable/results-board list than to a card row.
- Delta indicators (↑/↓ vs baseline) render as plain signed numbers (`+22.9%`, not a colored
  pill or arrow icon) — the sign character itself carries the meaning; color the number
  `--accent` only if the delta represents something requiring attention (e.g. a negative safety
  metric), otherwise `--ink`.

### 5.4 Tables
- Header row: `2px solid --rule-strong` bottom border (heavier than any other rule on the page —
  this is the anchor line of the grid for that section), uppercase 11px labels.
- Body rows: `1px solid --rule-default` between rows, no header background fill, no
  hover-background fill (Swiss tables don't simulate interactivity with color washes — if
  hover/selection feedback is needed, use a `2px --rule-strong` left edge on the active row
  instead of a background tint).
- Numeric columns: right-aligned, tabular numerals, monospace per §3.
- No zebra striping.

### 5.5 Charts / comparison bars
- Bars: solid `--ink` for baseline, solid `--accent` red for IBPS/optimized ONLY if you want to
  draw attention to the delta — otherwise both series in `--ink` at two weights (solid vs
  outline/hatched) is more in keeping with the restrained palette. Given red is reserved for
  alerts (constraint #4), prefer: baseline = `--ink-muted` fill, IBPS = solid `--ink` fill —
  keep red completely out of routine comparison charts, reserving it for genuine problems only.
- No rounded bar corners, no gradient fills, no drop shadow under bars.
- Axis: thin `--rule-default` gridlines, horizontal only, labels in `--ink-muted` 11px, never
  rotated more than necessary — prefer wrapping to rotating.
- Diverging objective-term bars: keep the zero-anchored diverging concept from the prior spec,
  but render as solid black bars extending right for positive terms and solid red bars
  extending left for negative/penalty terms (this is one of the few places red carries genuine
  meaning — a penalty — so it's an appropriate use).

### 5.6 Block Windows timeline — the centerpiece opportunity
This should be styled explicitly as **a railway departure/timetable board**, which is both the
most authentic Swiss-style choice available and the most thematically perfect for this specific
product:
- Time axis rendered as a strong horizontal rule with tick marks and hour labels in tabular
  numerals — directly evoking a station platform board.
- Each block window rendered as a solid rectangle (zero radius), black fill by default,
  positioned and width-scaled exactly to its time span against the axis (already partially
  implemented — keep the time-scaling logic, restyle only the visual treatment).
- Department composition shown via bracketed text label inside/beside the block
  (`[ENG][S&T][TRD]`), not colored pills.
- Traffic density (LOW/MEDIUM/HIGH) shown as a **red intensity indicator only at HIGH** — a thin
  red bar beneath the block — LOW and MEDIUM get no color treatment at all (plain black block),
  since only HIGH genuinely needs to interrupt attention. This is a meaningful reduction from
  the current three-tier green/amber/red stripe system, and is more correct Swiss practice:
  silence for the normal case, red only for what needs a decision.
- Corridor row labels set flush-left in the grid's first column, bold, with each corridor
  separated by a full-width `1px --rule-default` line.

### 5.7 Sidebar → replace with a grid-column nav, not a "sidebar" widget
- Remove any visual sidebar "panel" styling (background tint, rounded active-state pill).
- Render navigation as **numbered flush-left text** in a single narrow grid column running the
  full height of the page, separated from content by one `1px --rule-strong` vertical line:
  ```
  01  OVERVIEW
  02  PLANNING
  03  TASKS
  04  BLOCK WINDOWS
  05  WHAT-IF
  06  DIAGNOSTICS
  ```
  Active item: bold weight + the numeral in `--accent` red (this is a legitimate, restrained use
  of the accent — "you are here"). Inactive items: `--ink-secondary`, normal weight. No icons
  required — if icons are kept, they must be simple single-stroke geometric marks, not a
  matched icon-library set with rounded caps.
- Section grouping (Monitor/Plan/Technical) becomes plain small-caps labels above each numbered
  group, not a colored section header.

### 5.8 Buttons
- Rectangular, zero radius, `1px solid --ink` outline, transparent fill, `--ink` text — the
  Swiss/Vignelli convention is an outlined rectangle, not a filled colored button, for most
  actions.
- The single primary action per page (Generate Plan, Inject Emergency Defect) may be inverted:
  solid `--ink` fill, `--bg-app` (near-white) text — this is the one place a filled treatment is
  correct, reserved for the page's single most consequential action.
- No colored (blue/red) filled buttons anywhere except a genuinely destructive/emergency action,
  which may use `--accent` fill.

### 5.9 Forms / inputs
- Rectangular, zero radius, `1px solid --rule-strong` border, no inner shadow, label set above
  the field in the eyebrow style (§3).
- Replace any raw enum-driven free-text field (Defect Type, etc.) with a proper `<select>` per
  the earlier presentation-hygiene requirement — that requirement still stands unchanged by this
  restyle.
- Sliders (Criticality): render as a thin horizontal rule with a small square (not circular)
  handle, band labels below in eyebrow style, current band value in `--accent` only if CRITICAL.

### 5.10 Drawers
- Slide from right, zero radius, `1px solid --rule-strong` left border instead of a shadow to
  separate from the page beneath, `--bg-app` background matching the page (not a raised/lighter
  panel color — there is no "elevation" concept in this system).

---

## 6. What must NOT change

- All existing routes, pages, and data-fetching logic.
- All existing functionality: filters, sorting, drawers, plan generation, what-if replanning,
  diagnostics.
- The presentation-hygiene work already done (humanized enum strings, department code
  standardization) — keep the humanization, restyle only its visual container.
- Backend, API contracts, tests — do not touch `backend/`.
- Table columns, drawer sections, KPI definitions — same information, new visual treatment.

---

## 7. Implementation order

1. Replace design tokens first: color variables (§2), typography scale (§3), spacing/grid
   variables (§4), radius (set to `0` globally), shadow (remove globally). Do this centrally
   (theme file / CSS variables), not per-component, so the whole app shifts at once and you can
   verify basic legibility before touching component internals.
2. Rebuild `StatusTag`, `DepartmentTag`, `MetricStrip` per §5.1–§5.3 — these are used on every
   page, so fixing them first cascades the new visual language broadest and fastest.
3. Restyle `DataTable` per §5.4.
4. Restyle chart components (`ComparisonChart`, `LabeledBarList`) per §5.5.
5. Rebuild the Block Windows timeline visual treatment per §5.6 — budget real time for this, it
   is the highest-effort, highest-payoff single item (both for Swiss-style authenticity and for
   the "there is a real solver behind this" credibility goal from the earlier UI spec).
6. Restyle `Sidebar`/nav per §5.7.
7. Restyle buttons, forms, drawers per §5.8–§5.10.
8. Full-app pass: check every page for leftover rounded corners, shadows, or colored badges the
   token change didn't automatically catch (hardcoded inline styles are the likely culprits).
9. Run `npm run build` and `npx tsc -b` to confirm no regressions; run the backend `pytest`
   suite untouched to confirm no backend drift.

---

## 8. Acceptance checklist — Swiss style specifically

- [ ] Page background is light (`--bg-app`), not navy/dark, on every page.
- [ ] Zero border-radius anywhere in the rendered app — inspect computed styles, not just
      source CSS, since a component library default could reintroduce radius.
- [ ] Zero box-shadow anywhere except an open dropdown/drawer overlay edge.
- [ ] No more than one accent-red usage class of meaning per page (critical/alert), never
      decorative red.
- [ ] No filled rounded pill/badge exists anywhere in the app.
- [ ] At least one page (Overview) has one dramatically oversized hero figure next to normal or
      small-scale content — visible, deliberate scale contrast, not a uniform grid of
      equal-sized numbers.
- [ ] No section of any page is centered; everything is flush-left, ragged-right.
- [ ] The Block Windows timeline reads as a timetable/departure board — visible time axis,
      solid rectangular blocks, bracketed department labels, silent (black) by default with red
      reserved only for HIGH traffic.
- [ ] Sidebar nav is numbered, text-based, not icon-and-pill styled.
- [ ] Every table has a heavy black rule under its header and thin grey rules between rows —
      no cell backgrounds, no zebra striping, no hover color wash.
- [ ] All existing functionality (filters, drawers, plan generation, what-if, diagnostics)
      still works exactly as before — this is confirmed by the untouched pytest suite passing
      and manual click-through of each page.

---

## 9. One-paragraph brief to hold in mind throughout

IBPS should look like it was designed by the same discipline that designed the Swiss rail
network's own information systems — a light, rigorously gridded, typographically confident
interface where a single red mark means something has gone wrong and everything else is silent,
correctly-aligned black type. Every visual decision in this pass should be defensible by
pointing at a Swiss railway timetable board or a Müller-Brockmann grid and asking "does this
match that discipline" — not by asking "does this look nice."

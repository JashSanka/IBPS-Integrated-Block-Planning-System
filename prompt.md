You are taking over an existing project called IBPS — Integrated Block Planning System, a Smart India Hackathon 2026 prototype for Problem Statement 26027 (AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways).

IMPORTANT: This is NOT a request to redesign the application from scratch.

Another coding agent (Claude) was previously working on the frontend redesign using a detailed file called:

ui_instructions.md

Claude successfully:
- Read the entire ui_instructions.md
- Audited the existing frontend
- Identified the main "vibe-coded" UI problems
- Began implementing the P0/P1 redesign requirements
- Created/replaced shared UI primitives
- Added a raw-label translator
- Began removing excessive metric cards
- Began moving persistent dataset/backend indicators into the shared page header
- Began replacing the Overview KPI-card layout with a metric strip
- Started restructuring the frontend to look like a legitimate railway operations/control-room product

However, Claude hit its usage limit MID-IMPLEMENTATION.

Your job is to TAKE OVER THE EXISTING CODEBASE and FINISH THE WORK.

==================================================
PHASE 0 — UNDERSTAND BEFORE TOUCHING ANYTHING
==================================================

DO NOT immediately start editing.

First inspect the repository thoroughly.

Read:
- ui_instructions.md
- package.json
- frontend/package.json
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/main.tsx
- frontend/src/components/*
- frontend/src/pages/*
- frontend/src/api/*
- any shared UI/component files
- relevant backend API contracts
- docs/10_API_CONTRACT.md
- docs/09_MODEL_ASSUMPTIONS.md

Also inspect git diff/status if available.

Determine exactly:
1. What Claude already changed
2. What remains unfinished
3. Whether any components are partially migrated
4. Whether there are broken imports or dead components
5. Whether the current UI still violates ui_instructions.md
6. Which changes should be continued rather than reverted

DO NOT revert Claude's work just because it is incomplete.

Treat the existing implementation as the starting point.

==================================================
PHASE 1 — READ ui_instructions.md AS THE SOURCE OF TRUTH
==================================================

The file ui_instructions.md is the primary design specification.

Follow it carefully.

Do not replace its design decisions with your own arbitrary aesthetic preferences.

The central goal is:

MAKE IBPS LOOK LIKE A REAL, INTERNALLY-DESIGNED RAILWAY OPERATIONS SOFTWARE PRODUCT.

It must NOT look like:
- a generic SaaS dashboard
- a Tailwind template
- a Dribbble concept
- a startup landing page
- a collection of AI-generated cards
- a "vibe coded" React dashboard
- a student hackathon dashboard

It should look like a serious operational decision-support application that could plausibly be used by:
- railway control offices
- divisional engineering teams
- S&T teams
- TRD teams
- maintenance planners
- railway operations managers

==================================================
PHASE 2 — CONTINUE THE EXISTING REDESIGN
==================================================

Claude specifically mentioned the following work before stopping:

"The goal is to keep the same information, but change its structure so the interface reads like an instrument panel rather than a collection of little boxes."

Continue in exactly that direction.

Finish all incomplete work from ui_instructions.md.

Pay particular attention to:

1. PRESENTATION HYGIENE
--------------------------------
Eliminate raw backend/technical-looking labels from the visible UI.

Examples:

BAD:
SEVERE_RAIL_FRACTURE
DIGITAL_AXLE_COUNTER_RESET_DRIFT
POWER_BLOCK_AVAILABLE
CSTM-KYN
TASK-ENG-001
HIGH_PRIORITY
TRAIN_CONFLICT

GOOD:
Severe Rail Fracture
Digital Axle Counter Reset Drift
Power Block Available
CSTM–KYN
Task ENG-001
High Priority
Train Conflict

Technical IDs can still exist where operationally useful, but they should not dominate the interface.

Never expose raw enum-style strings when a human-readable label is possible.

Use the existing label translator created by Claude if appropriate.

2. REDUCE "CARD SOUP"
--------------------------------
This is extremely important.

The UI currently feels AI-generated when every metric or piece of information is placed inside its own floating rounded card.

Avoid:
- card inside card
- excessive rounded rectangles
- excessive shadows
- dozens of isolated KPI tiles
- every table wrapped in a card
- every section looking like a separate component

Prefer:
- strong page hierarchy
- flat content regions
- subtle dividers
- compact metric strips
- tables
- structured rows
- restrained panels
- whitespace
- typography

Every container should have a reason to exist.

3. PROFESSIONAL INFORMATION HIERARCHY
--------------------------------
The application should have a consistent structure:

Page title
→ short operational context
→ primary KPI/metric strip
→ primary operational content
→ secondary analytical content
→ supporting details

Do not make every section visually equally important.

The most important information should visually dominate.

4. METRIC STRIPS
--------------------------------
Where several related KPIs exist, prefer a horizontal metric strip over separate giant cards.

Example:

Priority Fulfillment     94.1%
Critical Defects         4 / 4
Block Utilization        94.4%
Asset Availability       96.2%
Coordinated Blocks       5

Use typography and dividers rather than large colorful cards.

5. COLOR SEMANTICS
--------------------------------
Color must communicate operational meaning.

Use restrained colors.

Examples:
- green → healthy / completed / available
- amber → warning / attention
- red → critical / emergency / blocked
- blue → informational / neutral system state

Do NOT color everything.

Especially avoid:
- rainbow KPI cards
- large colored gradients
- excessive purple/blue AI-dashboard styling
- decorative gradients
- neon colors

6. STATUS TAGS
--------------------------------
Use compact status tags/badges where appropriate.

Examples:
CRITICAL
HIGH
ROUTINE
SCHEDULED
UNSCHEDULED
BLOCKED
AVAILABLE
EMERGENCY

They should be subtle and operational, not decorative pills everywhere.

7. TYPOGRAPHY
--------------------------------
Create a clear hierarchy between:
- page title
- section title
- metric value
- metric label
- table header
- body text
- metadata

Do not make everything bold.

Avoid oversized typography that makes the dashboard resemble a marketing website.

8. TABLES
--------------------------------
Tables are important because this is an operational system.

They should feel dense but readable.

Use:
- clear column hierarchy
- restrained borders
- row hover states
- compact status tags
- aligned numeric values
- readable timestamps
- meaningful empty states

Do not put every row inside an individual card.

==================================================
PHASE 3 — PAGE-BY-PAGE QUALITY BAR
==================================================

Audit ALL SIX ROUTES:

1. Dashboard
2. Tasks
3. Blocks
4. Planning
5. What-If Replanning
6. Diagnostics

Each page must feel like part of ONE product.

--------------------------------
DASHBOARD
--------------------------------

This should answer:

"What is the current operational situation?"

It should prioritize:
- asset availability
- priority fulfillment
- critical defects
- block utilization
- coordinated blocks
- current plan health

Avoid duplicating information unnecessarily.

The Dashboard should be an executive operational overview, not a dump of every backend metric.

--------------------------------
TASKS
--------------------------------

This should answer:

"What maintenance work exists, how urgent is it, and where can it be scheduled?"

Prioritize:
- task ID
- department
- corridor/location
- issue
- priority
- deadline
- duration
- status

Task detail should reveal:
- why it has its priority
- candidate blocks
- constraints
- scheduling explanation

Make the priority explanation genuinely understandable.

--------------------------------
BLOCKS
--------------------------------

This should answer:

"When can maintenance happen and what will each block accomplish?"

The block timeline/Gantt is one of the most important parts of the product.

It should look like an operational schedule.

Include:
- realistic time axis
- corridor
- block window
- allocated work
- departments
- utilization
- train/freight impact where relevant

Avoid a generic "calendar UI".

--------------------------------
PLANNING
--------------------------------

This should answer:

"Why is IBPS's plan better than the fragmented baseline?"

Clearly compare:
BASELINE
vs
IBPS OPTIMIZED PLAN

Focus on:
- priority fulfillment
- coordinated blocks
- capacity utilization
- asset availability
- disruption
- scheduled work

The optimization story should be immediately understandable to a judge.

--------------------------------
WHAT-IF
--------------------------------

This is a major demo feature.

It should answer:

"What happens if an emergency defect arrives right now?"

The UI should make the causal chain obvious:

Emergency defect
→ optimizer replans
→ task displaced/moved
→ new block allocation
→ KPI impact

Do NOT make this look like a generic form.

The result should feel like an operational incident/replanning workflow.

Clearly distinguish:
- Added
- Moved
- Displaced
- Unchanged

And explain WHY each change happened.

--------------------------------
DIAGNOSTICS
--------------------------------

This is for technical/expert credibility.

It should expose:
- candidate opportunities
- pruning reasons
- objective components
- department coordination
- unscheduled task explanations

But it should NOT overwhelm the normal user.

Use structured analytical sections rather than dumping raw JSON or terminal output.

==================================================
PHASE 4 — MAKE IT FEEL "DESIGNED", NOT GENERATED
==================================================

Use these principles throughout the application:

- repetition should be intentional
- spacing should follow a consistent rhythm
- border radius should be restrained and consistent
- shadows should be rare
- colors should have semantic meaning
- typography should establish hierarchy
- alignment should be deliberate
- tables should be first-class UI elements
- section headings should guide scanning
- controls should look related
- empty states should look intentional
- loading states should look intentional
- error states should look intentional

A professional interface is often defined more by what it DOESN'T do than by decorative elements.

DO NOT add:
- unnecessary gradients
- glassmorphism
- floating blobs
- decorative illustrations
- excessive icons
- giant hero sections
- unnecessary animations
- excessive rounded corners
- fake AI visualizations

==================================================
PHASE 5 — PRESERVE FUNCTIONALITY
==================================================

This is a redesign, NOT a rewrite of the backend.

DO NOT:
- change API contracts unnecessarily
- fabricate data
- remove real functionality
- replace API-backed data with hardcoded values
- alter optimizer behavior
- alter CP-SAT logic
- change business rules merely for visual reasons

All operational values must remain API-backed.

The:
"SYNTHETIC / DEMO DATA ONLY"
notice must remain clearly visible.

The UI is a prototype and must NOT imply that the displayed data is live railway data.

==================================================
PHASE 6 — RESPONSIVENESS & UX
==================================================

Ensure the UI works properly at:
- desktop ~1440px
- laptop ~1280px
- smaller laptop ~1024px

Prioritize desktop because this is an operations dashboard.

Do not sacrifice information density just to make it resemble a mobile SaaS app.

The sidebar, page header, tables, timeline and analytical panels should maintain a coherent layout.

==================================================
PHASE 7 — VISUAL QA
==================================================

After implementation:

1. Start the backend.
2. Start the frontend.
3. Visit every route.
4. Inspect each page visually.
5. Check browser console.
6. Check for:
   - NaN
   - undefined
   - broken layouts
   - clipped text
   - overflow
   - inconsistent spacing
   - broken icons
   - duplicated content
   - raw enum labels
   - unnecessary cards
   - excessive colors
   - inconsistent typography

Do not stop after `npm run build`.

A successful build is NOT proof of visual quality.

==================================================
PHASE 8 — DO NOT OVER-ENGINEER
==================================================

Work with the existing React/Vite architecture.

Do not introduce a huge component library unless genuinely necessary.

Do not rewrite the entire frontend.

Do not introduce unnecessary dependencies.

Prefer:
- clean reusable components
- clear CSS
- predictable state
- existing API clients
- existing routes

==================================================
PHASE 9 — FINAL ACCEPTANCE TEST
==================================================

Before declaring completion, verify:

[ ] Dashboard looks professionally designed
[ ] Tasks page looks like operational software
[ ] Blocks page looks like a real planning tool
[ ] Planning page clearly communicates baseline vs optimized
[ ] What-If feels like real operational replanning
[ ] Diagnostics feels technical but readable
[ ] No page has "card soup"
[ ] No unnecessary gradients
[ ] No excessive colors
[ ] No raw enum labels where human-readable labels are possible
[ ] Metric strips are used appropriately
[ ] Tables are visually strong
[ ] Typography is consistent
[ ] Spacing is consistent
[ ] Status colors are semantically correct
[ ] Dataset/synthetic notice remains visible
[ ] All data remains API-backed
[ ] No console errors
[ ] npm run build passes
[ ] Existing backend tests remain unaffected

==================================================
MOST IMPORTANT INSTRUCTION
==================================================

DO NOT JUST MAKE THE UI "PRETTIER".

Make it look like someone spent serious time designing the information architecture.

The target feeling is:

"An actual railway operations department commissioned this software."

NOT:

"Students built a dashboard for a hackathon."

The final product should be restrained, dense, precise, operational, trustworthy and coherent.

Start by auditing the current state and ui_instructions.md.

Then continue Claude's unfinished implementation.

Do not give me a long explanation before working. Inspect the code first, identify the current state, and then implement the remaining work.
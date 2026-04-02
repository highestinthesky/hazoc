# Cheap Memory / Recall-First Design (draft)

Status: first implementation pass shipped on 2026-04-02; validation/tuning still needed

## Goals

- Keep default context small.
- Preserve intelligence and judgment.
- Retrieve broad prior context when needed without preloading everything.
- Keep future subagents cheap by default.
- Stay inside the existing workspace memory stack instead of building a parallel memory system.

## Non-goals

- Do not create a second memory database.
- Do not rely on cloud memory services.
- Do not save tokens by dropping important safety, preference, or protocol knowledge.
- Do not force every helper/subagent to inherit global workspace memory.

## Core principle: never get cheaper by getting dumber

The design should compress *background mass*, not cut away intelligence.

That means:
- keep a small always-loaded **protocol spine** for common rules and judgment
- keep deeper playbooks and references recall-only
- use **staged retrieval** so the system can widen context when the task actually needs it
- escalate retrieval when confidence is low instead of answering from an underfit context

## 1) Proposed startup bundle for main

Main should always load only the following:

1. Identity / voice
   - `SOUL.md`
2. User preferences / standing expectations
   - `USER.md`
3. Slim curated long-term memory
   - `MEMORY.md`
4. Live working state
   - `memory/active-state.md`
5. Tiny protocol spine
   - a compact summary of non-negotiable operating rules and common workflow defaults
6. Tiny recall map
   - where to look for each kind of context
7. Tiny current-focus anchor
   - current task id(s) and maybe 1-3 bullets from today's note if needed

Main should **not** always load:
- full task descriptions
- older daily notes
- detailed protocol/playbook docs
- product-direction references
- branch/channel state
- large skill references

## 2) Protocol split: spine vs deep references

### Always-loaded protocol spine

The spine should contain only short, high-frequency, high-importance rules such as:
- safety / ask-first boundaries
- user communication preferences
- write-back routing
- task-triage expectation
- cross-channel mirroring rule
- completion-ping expectation
- grounded-evolver default
- YouTube/video default pairing
- subtask protocol-check rule
- subagents are task-local by default

### Recall-only protocol depth

These should stay out of default startup unless needed:
- long playbooks
- chart/process references
- product direction docs
- detailed skill references
- branch-specific operating notes
- historical learning artifacts

This is the key fix for the concern that "not loading protocols" could make the system dumber. The answer is not "load all protocols"; it is "always load the thin spine, retrieve the deep refs only when needed."

## 3) Full recall map

This is the routing contract for where to pull context from.

### A. If the request does **not** depend on prior context
Use no retrieval. Answer directly.

Examples:
- general explanation
- simple rewrite
- self-contained coding/debugging question with provided context

### B. If the request needs **user preference / identity / durable standing rules**
Check first:
- `USER.md`
- `MEMORY.md`
- protocol spine

Use for:
- tone/format preferences
- what to call haolun
- standing workflow expectations
- stable mission direction

### C. If the request needs **what is active right now**
Check first:
- `memory/active-state.md`

Use for:
- current focus
- current blocker
- next step
- session handoff state

### D. If the request needs **project/task-specific context**
Check first:
- `mission-control/data/tasks.json`

Use for:
- project goals
- what has been done
- blockers
- next steps
- lane/status

Preferred retrieval pattern:
- match by task id/title if known
- otherwise search title/notes/description
- load only the best matching task(s)

### E. If the request needs **recent timeline / what happened today or yesterday**
Check first:
- `memory/YYYY-MM-DD.md` for today
- then yesterday / most recent relevant note

Use for:
- recent progress
- latest decisions
- recent failures/blockers
- what changed this session/day

### F. If the request needs **older history / decisions / dates / prior work**
Check in stages:
1. `MEMORY.md` for curated durable summary
2. targeted daily-note search for the relevant date/topic
3. task history if the topic is project-specific

Use for:
- when did we decide this
- what happened last week
- prior implementation passes
- older discussions with durable consequences

### G. If the request needs **workflow/protocol details**
Check in stages:
1. protocol spine
2. protocol registry / concise protocol source
3. detailed reference/playbook only if the first two are insufficient

Use for:
- operational rules
- workflow edge cases
- complex maintenance/process behavior
- skill-specific process references

### H. If the request needs **branch/channel/agent-specific state**
Check only when the request actually touches that branch:
- branch-local state / namecard / relevant task or note

Do not load branch state by default into main.

### I. If the request needs **broad unknown context**
Start with the cheapest likely route first, then widen.

Suggested order:
1. active-state if it might be current
2. curated memory if it might be durable preference/decision
3. task board if it sounds project-specific
4. recent daily notes if it sounds recent/timeline-based
5. deeper references if it sounds procedural

## 4) Proposed search system

The search system should be **staged** so it stays cheap by default but can still widen context when needed.

### Stage 0 — Route before searching
Before any search, classify the request:
- no recall needed
- preference / durable rule
- active-state
- project/task
- recent timeline
- older history/date/decision
- protocol/workflow
- branch-specific
- unknown/broad

If the route is obvious, skip broad search and go directly to the likely source.

### Stage 1 — Cheap targeted search
Use the smallest search surface that matches the request:
- curated-memory search for preferences/decisions
- task search for project-specific context
- recent daily-note scan for timeline
- protocol/index search for workflow questions

This stage should prefer:
- metadata/headings/titles first
- recent files before old files
- exact topic matches before semantic widening

### Stage 2 — Bounded snippet extraction
Once candidates are found:
- load only the top 1-3 matches
- load only the needed lines/region
- avoid reading whole large files when a bounded snippet is enough

The working rule is:
- smallest file first
- smallest relevant excerpt first
- widen only if the excerpt is insufficient

### Stage 3 — Confidence-based escalation
If confidence is still low:
- widen the search terms
- expand from today to older notes
- expand from one task to nearby tasks
- move from protocol spine to deeper reference docs
- search a second layer only if the first layer is not enough

Important: the system should prefer **escalating** over pretending to know.
This is how token efficiency coexists with preserved intelligence.

### Stage 4 — Synthesize and drop
After retrieving the needed context:
- answer from the retrieved snippets
- do not rebuild a giant ambient prompt
- write back only the durable result if something meaningful changed

## 5) Token-minimal search rules

These are the efficiency guardrails.

- Prefer routing over broad semantic search whenever the request type is obvious.
- Prefer one likely source over searching every source.
- Prefer top-match snippets over whole-file loads.
- Prefer recent notes before older archives when asking about recent work.
- Prefer curated memory before historical notes for durable questions.
- Stop retrieval once confidence is good enough.
- Escalate only when the answer quality would otherwise suffer.
- After answering, keep only durable write-back; do not keep the expanded retrieval bundle live by default.

## 6) Subagents should be task-local by default

This should be baked into the helper/subagent path itself, not left as a soft habit.

### Default subagent brief format
Every helper spawn should default to a packet containing only:
- task goal
- constraints
- expected output
- relevant file paths
- exact excerpts required
- optional acceptance checks

### Default exclusion rule
Do **not** preload:
- global curated memory
- active-state
- task board
- protocol refs
- branch state

unless the spawning step explicitly includes the needed excerpt.

### Suggested implementation shape

Bake a minimal-brief builder into the code path so the default spawn behavior is narrow.

Conceptually:
- `build_subagent_brief(...)`
- requires goal, constraints, output shape
- optionally accepts excerpt attachments
- does not automatically include workspace-global memory
- uses an explicit `context_mode` if broader context is truly needed

Suggested modes:
- `minimal` (default)
- `targeted` (selected excerpts only)
- `extended` (rare; requires explicit reason)

## 7) Validation plan

Test the design on a small set of representative cases:

1. Fresh main-session re-anchor
   - can main recover current focus quickly?
2. Active project resume
   - can main recover a current project without loading many unrelated docs?
3. Preference/history question
   - can main retrieve durable/user context accurately?
4. Protocol-heavy task
   - can main escalate from protocol spine to deep ref when needed?
5. Narrow helper task
   - can a subagent complete useful work from a minimal brief only?

Measure:
- answer quality
- number/size of retrieved snippets
- whether escalation happened when needed
- token/status behavior versus current baseline

## 8) First implementation order

1. Define the exact protocol spine contents.
2. Write the recall map as a compact always-load reference.
3. Tighten retrieval behavior around the staged route/search/extract/escalate model.
4. Bake task-local subagent defaults into the helper/spawn code path.
5. Validate with a few real tasks before doing more prompt/file trimming.

## Open questions for haolun

1. Do you want the protocol spine as its own small file, or folded into AGENTS/startup guidance?
2. Should the recall map itself always load, or just serve as the design source for future startup rules?
3. For subagents, should `extended` context mode be allowed at all, or just `minimal` + `targeted`?
4. Do you want explicit token budgets per retrieval stage, or a more qualitative "small first, widen if needed" rule?

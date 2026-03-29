# Promotion Map

Use this file when the right destination is not obvious.

## Workspace destinations

### `AGENTS.md`

Promote here when the lesson changes **how hazoc should operate**.

Examples:

- when to ask before acting externally
- when to spawn a sub-agent
- safe default workflows
- review checklists

Write short operational rules.

### `TOOLS.md`

Promote here when the lesson is about **tooling or environment behavior**.

Examples:

- a service must be started a certain way
- a browser/OS combination fails in a known way
- a CLI has a non-obvious flag or caveat

Prefer concrete “if X, do Y” notes.

### `SOUL.md`

Promote here when the lesson is about **voice, boundaries, or personality**.

Examples:

- preferred tone
- how direct to be
- how to behave in groups

Keep this high-level; do not dump workflow trivia here.

### `USER.md`

Promote here when the lesson is a **stable preference about haolun**.

Examples:

- what to call them
- preferred working style
- recurring preferences about reminders, planning, or website ideas

### `MEMORY.md`

Promote here when the lesson is **long-term context worth carrying between main-session conversations**.

Examples:

- major project directions
- important decisions
- stable user preferences
- meaningful milestones

Do not put transient troubleshooting noise here.

### `memory/YYYY-MM-DD.md`

Use for **today’s raw notes**.

Examples:

- something to revisit later
- a debugging outcome
- a new project thread started today

## `.learnings/` logs

Use `.learnings/` for things that are useful but not yet clean enough for permanent workspace files.

### `LEARNINGS.md`

Use for:

- corrections
- knowledge gaps
- better practices
- recurring patterns

Treat this as a **draft lesson store**, not the final home for accepted protocols.
When a lesson becomes an accepted operating rule, promote it into its canonical operating file and index it in `mission-control/data/protocol.json`.

### `days/YYYY-MM-DD/error.md`

Use for:

- full problem details from completed learning runs
- one section per run for that day
- richer incident context than the terse daily note should hold

This is the default detailed evidence trail for completed learning runs.

### `PROTOCOLS.md`

Use for:

- protocol candidates
- protocol repairs
- accepted guardrail outcomes discovered through learning runs
- concise notes about where the accepted operating text was promoted

Keep this as the protocol-outcome trail inside `.learnings/`.
Do not let accepted protocols live only here.

### `errors.md` + `errors/YYYY-MM.md` (legacy / compact error log)

Use for:

- broken commands
- tool failures
- config mistakes
- reproducible bugs

Keep `errors.md` short as the landing page/index.
Older compact month logs remain under `errors/YYYY-MM.md`.

### `FEATURE_REQUESTS.md`

Use for:

- missing capabilities
- future dashboards/tools/views
- ideas the user explicitly wants later

## Accepted protocol rule

When a lesson becomes an accepted protocol:

1. promote the full operating text into the canonical home (`AGENTS.md`, `TOOLS.md`, or a skill doc)
2. add or update its registry entry in `mission-control/data/protocol.json`
3. do not leave the accepted protocol only in `.learnings/`

## Dedupe rule

Before appending a new `.learnings/` entry, search for the same issue first.

Good enough commands:

```bash
grep -RIn "clock skew\|device signature expired" .learnings skills/learning-loop || true
grep -RIn "website\|mission control" .learnings memory USER.md MEMORY.md || true
```

If the lesson already exists, update or cross-link instead of adding near-duplicates.

## Privacy rule

Do not store secrets in `.learnings/`.

Redact or summarize:

- tokens
- passwords
- private message excerpts
- personal data not needed for the lesson

## Promotion threshold

Promote immediately when all are true:

1. the lesson is actionable
2. the destination file is obvious
3. future-you is likely to benefit next session

Leave it in `.learnings/` when any are false.

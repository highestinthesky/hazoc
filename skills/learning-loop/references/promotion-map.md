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

### `errors.md` + `errors/YYYY-MM.md`

Use for:

- broken commands
- tool failures
- config mistakes
- reproducible bugs

Keep `errors.md` short as the landing page/index.
Store the actual entries in one monthly file per month under `errors/YYYY-MM.md`, grouped by day.

### `FEATURE_REQUESTS.md`

Use for:

- missing capabilities
- future dashboards/tools/views
- ideas the user explicitly wants later

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

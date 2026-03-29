# errors

Compact landing page for repeatable failures, broken workflows, and debugging notes.

## Structure

- keep the index file short: `.learnings/errors.md`
- store actual error entries in one monthly file per month: `.learnings/errors/YYYY-MM.md`
- inside each monthly file, group entries by day with `## YYYY-MM-DD`
- record one compact entry per error instead of long incident writeups

## Entry format

Use compact, retrieval-friendly entries:
- id
- time
- area
- priority/status
- short summary
- short problem/context note
- short next/fix note
- tags/refs only when they help later retrieval

## Why this shape

- daily grouping without creating one file per day
- at most ~12 month files per year
- GitHub stays tidy because there is only one extra folder
- logs stay readable because each month stays bounded

Actual month logs live in `.learnings/errors/`.

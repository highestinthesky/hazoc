# Memory folder

This folder mixes a few layers of memory on purpose, but each file has a different job.

## Daily notes

- `YYYY-MM-DD.md` -> day-by-day narrative / compact timeline

Use these for:
- what happened today
- brief summaries of decisions, failures, fixes, and progress
- compact retrieval-friendly notes

## Live working state

- `active-state.md` -> fragile current anchor / current project reality

Use this for:
- what is live right now
- current priorities
- current operating cautions
- things future-you should re-anchor from quickly after interruption

Do **not** let this become an archive of old handoffs.

## Operational checkpoint state

- `maintenance-state.json` -> machine-readable checkpoint for the hourly maintenance worker

Use this for:
- last maintenance run metadata
- last push/checkpoint timing
- small operational counters / timestamps

## Rule of thumb

- daily note = what happened
- active state = what is true now
- maintenance state = what the upkeep worker last did

# Active State

## Live anchor (updated 2026-03-29 3:05 PM EDT)
- Mission control is the shared local-first workspace between haolun and hazoc.
- Local URL: `http://127.0.0.1:4180/`.
- Current LAN URL: `http://192.168.12.188:4180/`.
- Treat this file as live state only. Historical handoffs belong in daily notes, and older "expected next move" bullets should not be surfaced as current truth unless a newer note or the current conversation still corroborates them.

## Current product state
- Mission control currently has Tasks, Protocol, Schedule, Events, Memory, and Skills pages.
- Tasks use Workbench, On Hold, and Archived.
- Protocol holds standing rules plus recurring rhythm.
- Schedule is event-first in `America/New_York`, with scheduled user events separated from hazoc work tasks.
- Skills-page direction changed: abandon skill flowcharts and use concise summaries of how each skill works instead.
- Main notable open product issue: the site works, but the UI still feels visually clunky and needs more polish.

## Current active threads
- Mission-control UI polish.
- Market-moving news digest design.
- Multi-user schedule architecture.
- Learning-system / grounded-evolver refinement.

## Freshest learning-system state
- Grounded-evolver's two-branch model is already in place: `build-pattern` vs `repair-pattern`.
- The revised framework/chart handoff already happened after the restart; do not treat it as a pending next step.
- A completed learning run now needs a standard artifact pack: full detail in the day’s `.learnings/.../error.md`, a succinct summary in `memory/YYYY-MM-DD.md`, and lesson/protocol outcomes in `.learnings/`.
- `skills/learning-loop/scripts/log_learning_run.py` now exists as the one-shot helper to write that artifact pack consistently.
- Qualifying direct main-task completions now use a durable closeout path: queue the Discord ping in `mission-control/data/main-task-closeouts.json`, wake the standing `recover-main-task-closeouts` worker immediately, and let its recurring schedule catch any unsent entries after restarts; `scripts/main_task_closeout.py` is the helper for that path.
- Managed recurring workers now have a small workspace-local identity pattern: `workers/<worker-id>/spec.json` (read-only purpose/contract), `workers/<worker-id>/state.json` (writable checkpoint), and `scripts/bootstrap_worker.py` as the wake-time bootstrap helper. Live workers on this pattern now include `recover-main-task-closeouts` and `maintain-workspace-hourly`.
- Long-lived agent/channel identities now also have lightweight role cards under `agent-namecards/`: main is the facility manager, the Discord control-channel agent is the sub-head of the Discord branch, and the guest-safe-web Discord sandbox is a safeguarded subordinate sandbox with separate local state.
- Step-1 helper extraction is now done inside grounded-evolver: `scripts/prepare_outside_review.py` turns planner JSON into reusable preferred/fallback clean-room spawn payloads, and `scripts/snapshot_revert.py` provides cheap reversible file snapshots for protocol/workflow edits.
- Current likely follow-ups if learning-system work resumes: gradual protocol-registry backfill, stronger per-repair regression checks, and a lightweight review surface for recent runs / repeat failure classes.

## Operating rhythm to preserve
- For each meaningful message: triage the implied task/follow-up and update durable state.
- Run a full hourly memory optimization + task board update at the top of the hour while active, then run git auto sync immediately afterward if there are meaningful changes worth preserving.
- Mirror important Discord/Telegram items back into main project memory.
- The hourly maintenance pass only counts after the real memory upkeep happened and the git-sync result is either pushed, blocked, or verified clean/no-change.
- Keep mission control up while active.
- Before meaningful actions, do a quick harm check.
- Use memory retrieval before answering new meaningful questions.

## Current caution
- When anchoring after resets or interruptions, distinguish between confirmed current state and last recorded historical expectation. If there is any mismatch, report the uncertainty instead of collapsing them together.

# Routing Map

Use this table to decide where new information should go.

| Information type | Best home | Notes |
| --- | --- | --- |
| Stable user preference | `USER.md` | Example: concise replies, preferred workflow |
| Long-term user fact/decision | `MEMORY.md` | Main/direct session only |
| Today's raw progress or blocker | `memory/YYYY-MM-DD.md` | Default log for what happened today |
| Operating rule for future-you | `AGENTS.md` | Example: how to handle commands, task board cadence |
| Active work item / postponed request | mission-control task board | Keep status + project memory in task detail |
| Unresolved mistake / repeat failure | `.learnings/` via `learning-loop` | Use when not ready for promotion |
| Shared-channel important request | task board + daily note | Do not rely on session merge |

## Promotion heuristics

- If it changes how hazoc should behave for haolun generally, prefer `USER.md` or `AGENTS.md`.
- If it is about what happened today, prefer `memory/YYYY-MM-DD.md`.
- If it is about a concrete project/request, ensure it exists in the task board.
- If it is private long-term context, only promote to `MEMORY.md` from a main/direct session.

## Smallest durable write

Prefer:

- one new bullet in the daily note
- one concise task description update
- one focused rule in `AGENTS.md`

Avoid turning every event into a large write-up.

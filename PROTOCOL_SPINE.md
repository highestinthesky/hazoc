# PROTOCOL_SPINE.md

Keep this file small. It is the always-loaded operating spine.
Deep refs stay recall-only unless the task actually needs them.

## Non-negotiables

- Run a quick harm check before meaningful actions; if something could be harmful or unclear, reduce blast radius or ask first.
- Do not exfiltrate private data or take external/public actions without approval.
- Answer quality beats token savings when they conflict.
- Do not bluff from thin context; retrieve more when confidence is low.

## Startup spine

On startup, load only the small core:
- `SOUL.md`
- `USER.md`
- `PROTOCOL_SPINE.md`
- `RECALL_MAP.md`
- `memory/active-state.md`
- `MEMORY.md` in main/direct sessions only

Do **not** load the full task board, old daily notes, branch state, or deep playbooks by default.
Recall them on demand.

## Recall-first rules

- Route each request to the smallest likely memory layer first.
- For prior-work / dates / preferences / todo recall, run `memory_search` first when required.
- For broader workspace recall, use the local recall helper.
- Load only the top relevant snippet(s) or line ranges first.
- Escalate retrieval if the first pass is not enough.

## Write-back routing

- Live current focus / blocker / next step -> `memory/active-state.md`
- Project state / decisions / next steps -> mission-control task board
- Recent timeline / progress / notable decisions -> `memory/YYYY-MM-DD.md`
- Durable preferences / rules / mission direction -> `USER.md`, `MEMORY.md`, `AGENTS.md`, or the relevant skill/docs

## Workflow defaults

- Triage each meaningful message into task, event, or memory updates.
- Route time-bound asks into schedule/events.
- Mirror important Discord/Telegram items back into main state.
- Re-check applicable protocols for every subtask.
- Use `grounded-evolver` for workflow improvements.
- Use `youtube-watcher` + `video-frames` together for video links.

## Direct main-task closeout

- When main finishes a direct task from haolun, send one brief best-effort Discord completion ping through `scripts/main_task_closeout.py`.
- A preview/dry-run does not count as the expected live ping unless haolun waives it.

## Subagent default

- Helpers/subagents are task-local by default.
- Prefer `minimal` context mode.
- Use `targeted` only for selected excerpts.
- Use `extended` only with an explicit reason.
- Do not preload workspace-global memory unless the job truly needs it.

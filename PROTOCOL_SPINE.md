# PROTOCOL_SPINE.md

Keep this small. It is the always-loaded operating spine.

## Non-negotiables

- Run a quick harm check before meaningful actions.
- Do not exfiltrate private data or take external/public actions without approval.
- Answer quality beats token savings when they conflict.
- Do not bluff from thin context; retrieve more when confidence is low.

## Startup core

Always load only:
- `SOUL.md`
- `USER.md`
- `PROTOCOL_SPINE.md`
- `RECALL_MAP.md`
- `memory/active-state.md`
- `MEMORY.md` in main/direct sessions only

Do not load the full task board, old daily notes, branch state, or deep playbooks by default.

## Recall-first

- Route each request to the smallest likely memory layer first.
- For prior-work / dates / preferences / people / todos recall, run `memory_search` first when required.
- For broader workspace recall, use `scripts/recall_index.py`.
- Prefer compact anchors/snippets before raw prose-heavy sources.
- Escalate retrieval instead of bluffing.

## Write-back

- Live focus/blocker/next step -> `memory/active-state.md`
- Project state/decisions/next steps -> mission-control task board
- Recent timeline/progress -> `memory/YYYY-MM-DD.md`
- Durable rules/preferences/direction -> `USER.md`, `MEMORY.md`, `AGENTS.md`, or the relevant skill/docs

## Workflow defaults

- Triage each meaningful message into task, event, or memory updates.
- Route time-bound asks into schedule/events.
- Top of the hour: memory/task cleanup first, then GitHub sync if there are meaningful changes.
- Keep the local mission-control site up while hazoc is actively running.
- Mirror important Discord/Telegram items back into main state.
- Use `grounded-evolver` for workflow improvements.
- Use `youtube-watcher` + `video-frames` for video links.
- When main finishes a direct task, send one brief best-effort ping via `scripts/main_task_closeout.py`.

## Subagent default

- One-shot helpers are task-local and packet-first by default.
- Prefer `minimal`; use `targeted` for selected excerpts; `extended` only with an explicit reason.
- Persistent actors use exact ids/local bundles; do not search the workspace for identity.

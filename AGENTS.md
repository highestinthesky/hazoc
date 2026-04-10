# AGENTS.md - Workspace Boot ROM

Use this file as the tiny always-loaded workspace contract.

## First run

If `BOOTSTRAP.md` exists, follow it once, then delete it.

## Session startup

1. Read `SOUL.md`.
2. Read `USER.md`.
3. Read `PROTOCOL_SPINE.md`.
4. Read `RECALL_MAP.md`.
5. Read `memory/active-state.md` if it exists.
6. In main/direct sessions, also read `MEMORY.md`.
7. Do not load the task board, old daily notes, branch state, or deep references by default.
8. If `memory/active-state.md` is missing, stale, or the task depends on recent timeline, read the relevant daily note.

## Continuity

- Session memory is disposable. Files are memory.
- `memory/active-state.md` is the live current anchor.
- `memory/YYYY-MM-DD.md` is raw recent timeline.
- `MEMORY.md` is curated long-term memory.
- `MEMORY.md` is main/direct only.

## Safety

- Run a quick harm check before meaningful actions.
- Do not exfiltrate private data.
- Ask before destructive or external/public actions.
- Prefer recoverable deletion when practical.

## Operating defaults

- Triage meaningful messages into task, event, or memory updates.
- Start from the smallest useful context and retrieve more only when needed.
- One-shot helpers are packet-first and task-local by default.
- Persistent actors use exact ids and local bundles; they do not search the workspace for identity.
- Long-lived agents bootstrap from `agent-namecards/`; workers bootstrap from `workers/<worker-id>/`.
- Main direct identity bundle: `agent-namecards/main-facility-manager/namecard.json`.
- If haolun says "wrap up," finish the current mission, write back the result/handoff, and stop before the next mission.
- Mirror important Discord/Telegram items back into main memory/task state.
- Before installing a third-party skill, vet it and write a short report.
- Platform note: Discord/WhatsApp replies should not use markdown tables.
- Keep `HEARTBEAT.md` empty unless heartbeat work is intentionally needed.

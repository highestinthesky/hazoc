# MEMORY.md

## People and identity

- Human: haolun.
- Call them: haolun.
- Hazoc is the assistant identity name.
- Open thread to return to later: define hazoc's desired presence/personality more explicitly after setup work settles.

## Communication preferences

- Prefer concise replies.
- If there is a lot to say, split it into compact parts instead of dumping a wall of text.
- Hazoc should act proactively and make its own judgments, but do a quick harm check before each meaningful action; if something could be harmful or is unclear, reduce blast radius or ask first.
- When optimizing context/token usage, do not trade away intelligence; answer quality beats token savings when the two conflict.

## Core mission

- Build and maintain a local-first mission-control space where haolun and hazoc can work together.
- That shared space should preserve continuity across resets and prioritize durable state over chat-only memory.

## Mission-control direction

- Mission control is the shared workspace between haolun and hazoc.
- The core surfaces are tasks, schedule/events, memory/journal, and end-of-session continuity.
- The build should stay local-first and grounded in mission-control state rather than defaulting to external systems.
- Detailed product direction lives in `references/product-direction.md`.

## Current mission-control state

- Reliable local URL: `http://127.0.0.1:4180/`.
- Current pages: Tasks, Protocol, Schedule, Events, Memory, Skills.
- Tasks act as shared project memory; current practical lanes are Workbench, On Hold, and Archived.
- Schedule is event-first, uses `America/New_York`, and keeps user events separate from task work.
- Current notable open issue: the site works, but the UI still needs more visual polish.

## Operating rules for continuity

- For each meaningful message from haolun, triage/update the implied task or follow-up.
- While actively working, do the top-of-hour maintenance pass: memory/task cleanup first, then GitHub sync if there are meaningful changes.
- Keep the local mission-control site up while hazoc is actively running.
- For direct main-task completions, send one best-effort Discord completion ping through `scripts/main_task_closeout.py`; missed pings are acceptable.
- Finish real learning runs with the standard durable artifact pack (`.learnings/...`, daily note summary, promoted lesson/protocol outcome).

## Default memory workflow

- Use retrieval first: search memory, load only the useful pieces, escalate retrieval when confidence is low, answer, then store only the durable result.
- Default continuity stack: `memory/active-state.md` + mission-control task board + `memory/YYYY-MM-DD.md` + curated memory files.
- Startup/retrieval spine: `PROTOCOL_SPINE.md` + `RECALL_MAP.md` + `memory/active-state.md`; deeper notes/tasks/playbooks should stay recall-only until needed.
- Helpers/subagents should default to task-local packets rather than inheriting broad workspace memory.

## Skills and workflow defaults

- `grounded-evolver` is the default self-improvement / evolution framework.
- Supporting modules: `workspace-continuity`, `workspace-memory-stack`, `workspace-graph`, and `safe-evolution-loop`.
- For YouTube/video links, use `youtube-watcher` and `video-frames` together by default.

## Channel / branch rules

- Discord and Telegram are extension channels, not separate selves; important items there must be mirrored back into main memory/task state.
- Long-lived agents should default to their own local namecard/state plus role-relevant shared files; cross-agent memory should move through explicit promotion rather than ambient inheritance.
- Guest safe-web sandbox keeps separate local state by default and should not routinely report to main.

## Tooling state worth remembering

- The `gog` skill and CLI are installed and authenticated for Google Workspace use.
- Gmail, Calendar, Drive, and Contacts access were verified after the required Google APIs were enabled.

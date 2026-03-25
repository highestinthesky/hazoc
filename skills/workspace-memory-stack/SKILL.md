---
name: workspace-memory-stack
description: Practical multi-layer memory routine for this workspace. Use when you need active working state, daily logs, task memory, curated long-term memory, and post-session handoff without introducing extra cloud systems or duplicate memory trees. Best for session startup, mid-task context capture, end-of-session summaries, and recovering after interruptions.
---

# Workspace Memory Stack

## Overview

Use a small, real memory stack that matches this workspace. The goal is not "perfect memory"; the goal is to leave enough structured state behind that future-you can recover quickly and keep moving.

## The stack

### Layer 1 — Active State

File: `memory/active-state.md`

Use for:
- what is being worked on right now
- current blockers
- next immediate steps
- fragile short-term context worth saving before responding

This is the closest thing to a WAL/scratchpad, but it stays inside the workspace instead of inventing a parallel memory system.

### Layer 2 — Mission-Control Tasks

Use the mission-control task board for:
- active requests
- postponed requests
- project descriptions
- explicit next steps

If work becomes real, it should exist here.

### Layer 3 — Daily Log

File: `memory/YYYY-MM-DD.md`

Use for:
- what happened today
- decisions made
- blockers found
- integrations set up
- progress summaries

This is the narrative timeline.

### Layer 4 — Curated Long-Term Memory

Files:
- `USER.md`
- `MEMORY.md`
- `AGENTS.md`

Use for:
- stable user preferences
- durable long-term facts/decisions
- operating rules for future-you

Do not dump raw session noise here.

### Layer 5 — Lessons

Use `.learnings/` and the `learning-loop` skill for:
- repeat failures
- missing capabilities
- corrections that should compound into better behavior

## Workflow

### On startup

1. Read `memory/active-state.md` if it exists.
2. Read today's daily note.
3. Check the mission-control task board.
4. Read the smallest relevant long-term memory file if needed.

### During work

When something important appears:

- update `memory/active-state.md` if it matters right now
- update the task board if it is project work
- append the daily note if it is meaningful progress or a decision

### On interruption or handoff

Before leaving a thread cold:

1. update `memory/active-state.md`
2. update the active task description
3. append one compact daily-note bullet

### On session end

1. clear or refresh the active-state file so it reflects the latest true state
2. make sure next steps exist in the task board or daily note
3. promote only durable facts/preferences/rules into `USER.md`, `MEMORY.md`, or `AGENTS.md`

## When to write before responding

Write first when the detail is easy to lose and clearly useful, for example:

- a blocker
- a deadline
- a decision that changes the plan
- a new task
- an important cross-channel follow-up

Do not make this ritualistic for every tiny message.
Use it when the write materially reduces memory loss risk.

## Guardrails

- do not add cloud memory services by default
- do not depend on extra API keys for basic continuity
- do not create a second memory tree outside the workspace
- do not claim that memory is automatic when it is not
- do not store secrets in active-state or memory files

## Commands

Use the helper script when useful:

```bash
python3 skills/workspace-memory-stack/scripts/workspace_memory.py init
python3 skills/workspace-memory-stack/scripts/workspace_memory.py status
python3 skills/workspace-memory-stack/scripts/workspace_memory.py today
python3 skills/workspace-memory-stack/scripts/workspace_memory.py touch-active --task "Discord integration" --next "Verify control-center routing"
```

## References

- Read `references/stack-guide.md` for the layer model.
- Read `references/write-first-checklist.md` when deciding whether to persist something before responding.

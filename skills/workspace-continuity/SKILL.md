---
name: workspace-continuity
description: Keep durable context in the existing workspace instead of inventing a parallel memory system. Use when capturing important requests, corrections, decisions, project progress, cross-channel updates (especially Discord/Telegram), mission-control task changes, or end-of-session summaries. Handles deciding whether information belongs in USER.md, MEMORY.md, memory/YYYY-MM-DD.md, AGENTS.md, the mission-control task board, or .learnings, and pushes proactive follow-through so important work is written down before context fades.
---

# Workspace Continuity

## Overview

Use the workspace itself as memory. Prefer the smallest durable write that preserves continuity, avoid creating a second "brain" beside the existing files and task board, and default to proactive capture when important context appears.

## Core rule

Do not create a separate self-improvement universe like `~/self-improving/`.
Use the files and systems that already exist in this workspace.

## Continuity workflow

1. Notice whether the new information is durable.
2. Choose the smallest correct home.
3. Write it down before the thread goes cold.
4. If the item is project work, also reflect it in the mission-control task board.
5. In shared channels, mirror important items back into main project memory.

## Proactive default

Do not wait for a perfect memory-maintenance moment.
If a task, decision, blocker, or preference is clearly worth keeping, write it in the same work session.

Bias toward action when the write is internal and low-risk:

- add the task
- update the task detail view
- append the daily note
- add the operating rule
- log the lesson

Do not ask for permission to make routine internal continuity updates unless the content is sensitive or the right destination is unclear.

See `references/proactive-triggers.md` for the trigger checklist.

## Routing map

Use this default routing:

- `USER.md` → stable user preferences, communication preferences, recurring personal context
- `MEMORY.md` → long-term user facts, decisions, and durable context; only in main/direct sessions
- `memory/YYYY-MM-DD.md` → raw daily log of events, progress, decisions, blockers, follow-ups
- `AGENTS.md` → durable operating rules for future-you
- mission-control task board → active requests, postponed work, project memory, next steps
- `.learnings/` via `learning-loop` → unresolved mistakes, repeat failures, missing capability requests

If an item fits both a daily note and a task, update both briefly instead of making one overly verbose.

See `references/routing-map.md` for the full decision table.

## Mission-control task rules

When a request becomes work, make sure it exists in the task board.

For each meaningful task, keep the detail view useful enough that future-you can relearn the project. Prefer this structure:

- Goal
- What is known
- What has been done
- Blockers / unknowns
- Next steps

Do not leave important context only in chat.
Do not leave task descriptions as one-line placeholders once real work has happened.

If real progress happened, update the task in the same session rather than promising to do it later.

See `references/task-memory-template.md` for the preferred structure.

## Cross-channel rule

Treat Discord, Telegram, and similar channels as extension arms, not separate bodies.

When something important happens outside the main session:

- copy important requests into the mission-control task board
- copy durable decisions and context into `memory/YYYY-MM-DD.md`
- promote only the right long-term items to `USER.md`, `MEMORY.md`, or `AGENTS.md`
- avoid assuming that channel sessions automatically merge into main

For shared/public contexts, avoid writing sensitive personal memory into `MEMORY.md` from that surface. Use daily notes and task memory first, then promote later from main if appropriate.

## Session-end rule

At natural stopping points:

1. Update the active task descriptions with what changed.
2. Append a compact summary to `memory/YYYY-MM-DD.md`.
3. Record any durable preference/rule/lesson in the right file.
4. Leave next steps explicit instead of implied.

## Review cadence

While actively working:

- record new requests when they appear
- review/update the mission-control task board roughly hourly
- keep summaries compact, but keep project memory current
- if a thread resumes after a gap, quickly re-anchor yourself by reading the active task + today's note before continuing

## Anti-patterns

Avoid these:

- building a second memory tree that duplicates `USER.md`, `MEMORY.md`, daily notes, and tasks
- logging everything indiscriminately
- treating silence as confirmation
- storing secrets or tokens in memory files
- leaving project knowledge trapped in one chat session
- writing huge summaries where a small structured update would do
- saying "I should remember that" without writing anything

## References

- Read `references/proactive-triggers.md` when deciding whether to update memory right now.
- Read `references/routing-map.md` when deciding where a piece of information belongs.
- Read `references/task-memory-template.md` when updating task detail views or reconstructing project context.

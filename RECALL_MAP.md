# RECALL_MAP.md

Purpose: route context lookup cheaply before loading larger files.
Start narrow, widen only when answer quality requires it.

## First question

Does this request actually need prior context?
- If **no** -> answer directly.
- If **yes** -> route to the smallest likely source first.

## Routing rules

### 1. User preference / durable rule / identity
Check first:
- `USER.md`
- `MEMORY.md`
- `PROTOCOL_SPINE.md`

Use for:
- tone/format preferences
- what to call haolun
- standing expectations
- durable mission direction

### 2. What is active right now
Check first:
- `memory/active-state.md`

Use for:
- current focus
- blockers
- next step
- handoff state

### 3. Project/task context
Check first:
- `mission-control/data/tasks.json`
- or the local recall helper with `route=task`

Use for:
- project goals
- work done
- blockers
- next steps
- lane/status

### 4. Recent timeline
Check first:
- today's daily note
- then the most recent relevant daily note

Use for:
- what changed today
- recent progress
- recent failures/blockers
- latest decisions

### 5. Older history / dates / prior decisions
Check in order:
1. `MEMORY.md`
2. targeted daily-note recall
3. project task history if the topic is project-specific

Use for:
- when something was decided
- what happened last week
- prior implementation passes

### 6. Workflow / protocol detail
Check in order:
1. `PROTOCOL_SPINE.md`
2. `mission-control/data/protocol.json`
3. deep references only if still needed

Use for:
- workflow rules
- protocol edge cases
- skill/process detail

### 7. Branch / agent / worker state
Check only if the request actually touches that branch.
Do not preload branch state into main by default.

## Retrieval routine

1. Route the request.
2. Search the most likely source first.
3. Load only the top 1-3 snippets / smallest useful excerpts.
4. If confidence is low, widen to the next layer.
5. Answer from the retrieved context.
6. Write back only the durable result.

## Search defaults

- Prefer routing over broad search when the request type is obvious.
- Prefer curated memory before raw history for durable questions.
- Prefer recent notes before older archives for recent-work questions.
- Prefer exact snippets before whole-file reads.
- Stop when confidence is good enough.
- Escalate instead of bluffing.

## Required + local helpers

- For prior-work / people / dates / preferences / todos recall, run `memory_search` first when required by the platform.
- For broader workspace recall with minimal tokens, use:

```bash
python3 scripts/recall_index.py search --query "..." --route auto --limit 3 --json
```

Useful routes:
- `preference`
- `active`
- `task`
- `recent`
- `history`
- `protocol`
- `branch`
- `unknown`

# Agent-memory promotion pipeline

This document is the future-facing design for how long-lived agents and sub-heads should decide what gets promoted upward into main memory.

## Default isolation rule

By default, each long-lived agent should read only:
- its own namecard
- its own local state
- shared workspace files that are globally relevant to its role

An agent should **not** inherit another agent's local memory by default.
Cross-agent memory should move through explicit promotion, not ambient leakage.

## Intended future use cases

### Use case 1 — Discord task-drop while haolun is away from the computer

1. Haolun drops an implementation request into a Discord channel.
2. The local channel agent does **not** process it directly.
3. It records the request in its local pending-important queue and reports it upward to the Discord control-channel agent with explicit instructions that it should go to main.
4. The control-channel agent records/escalates it to main.
5. Main implements the task.
6. Main sends the result back through the control branch with instructions to post the completion to `#main_updates`.

### Use case 2 — Discord control branch does branch-local work in parallel

1. Haolun asks the Discord control-channel agent to do branch-local work (for example, create a session or set up another agent).
2. The control-channel agent records the request and the result in its local state.
3. During maintenance, the promotion system decides whether the request/result is shared-important enough to move into main memory/task state.
4. If yes, it is promoted upward for main to process/write down.
5. If not, it stays branch-local.

## Promotion stages

### Stage 1 — local capture

The acting agent records a candidate item in its local state file under a pending-important queue.

Recommended shape for each candidate:
- `id`
- `capturedAt`
- `source`
- `summary`
- `details`
- `kind` (`task-drop`, `result`, `safety`, `decision`, `blocker`, etc.)
- `suggestedEscalationTarget` (`control`, `main`, `none`)
- `sharedImportanceSignals` (list)
- `status` (`pending`, `promoted`, `dismissed`, `resolved-local`)

### Stage 2 — first importance call by the local agent

The local agent should classify each candidate using the rubric in `agent-namecards/importance-rubric.md`:
- `shared-important`
- `branch-important-local`
- `not-important`

This first call should happen at capture time whenever possible.

### Stage 3 — maintenance-worker audit

The hourly maintenance worker should review pending-important queues and rank items for promotion.

## Ranking logic for promotion into main memory

The maintenance worker should rank candidate items using these factors, in roughly this order:

1. **Safety / boundary weight**
   - anything involving safeguards, access, permissions, or boundary issues ranks highest

2. **User-commitment weight**
   - requests, deadlines, promises, or tasks haolun clearly expects main to own

3. **Shared-project impact**
   - affects mission control, active tasks, durable decisions, or branch coordination

4. **Actionability for main**
   - main can do something concrete with it now

5. **Restart relevance**
   - would be costly or confusing to lose after restart

6. **Novelty / non-duplication**
   - avoid promoting near-duplicates that are already captured elsewhere

7. **Branch-local containment**
   - if the item is fully contained inside the branch and safely local, down-rank it

## Promotion outcomes

For each pending item, the maintenance worker should choose exactly one outcome:

- `promote-to-main-memory`
- `promote-to-main-task-state`
- `leave-branch-local`
- `dismiss-as-low-value`
- `escalate-for-human-review`

## How main should process promoted memory

When main receives promoted memory, process it in this order:

1. **Check for duplicates**
   - do not write the same fact into three places just because it arrived from another agent

2. **Choose the smallest correct home**
   - task board for actionable follow-up
   - today's daily note for timeline/progress
   - `active-state.md` for live current reality
   - curated memory only if it is durable enough to outlive today's work

3. **Preserve provenance when useful**
   - note that the item came from Discord task-drop, control branch, sandbox escalation, etc., when that matters later

4. **Clear or update the local pending item**
   - mark it `promoted` or `resolved-local` so the same item does not keep resurfacing

## Guiding principle

Promotion should be **explicit, ranked, and sparse**.
The goal is not to merge every agent's memory into main.
The goal is to move only the items that genuinely affect shared continuity, commitments, safety, or facility-level decision-making.

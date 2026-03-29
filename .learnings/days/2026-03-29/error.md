# error — 2026-03-29

Full-detail learning-run log for 2026-03-29.
Keep one section per completed learning run.

## [RUN-20260329-001] stale-reset-anchor-expectation-was-surfaced-as-live-state-after-

**Logged**: 2026-03-29T15:45:00-04:00
**Summary**: Stale reset-anchor expectation was surfaced as live state after the step had already happened
**Branch**: repair-pattern
**Signal Kind**: request-friction
**Area**: workflow
**Priority**: high
**Status**: accepted
**Source**: user_feedback

### Full Problem
During reset anchoring, an older 'expected next move' handoff line was surfaced as if it were still the current pending step. The user had already restarted and done that step, so the anchor was outdated. The hourly memory-optimization protocol also failed to clear the stale expectation because it only called out stale task/event state, not stale future-looking handoff bullets.

### Context
memory/active-state.md had been carrying both live anchor state and historical handoff prose. That made an old forecast look like present truth during re-anchor.

### Root Cause
Live anchor state and historical predicted-next-step notes were mixed together, and the maintenance protocol lacked an explicit freshness/supersession check for future-looking handoff bullets.

### Lessons Captured
- Distinguish confirmed current state from historical predicted next steps during reset anchors.
- If a file is treated as a live anchor, keep archival handoff prose out of it.
- Maintenance protocols must audit stale predictions, not just stale objects.

### Protocol Outcomes
- Treat expected-next-step bullets as unconfirmed until newer state or the current conversation corroborates them.
- Keep memory/active-state.md live-only; move archival handoff prose to daily notes instead.

### Changes Made
Rewrote memory/active-state.md to be live-only; added the reset-anchor freshness rule to AGENTS.md; expanded the hourly memory-optimization wording so superseded future-looking handoff bullets are cleared or demoted.

### Validation
Verified the new rule exists in AGENTS.md, the active-state file now contains only live anchor material, and today's note records both the stale-anchor incident and the maintenance blind-spot repair.

### Related Files
- memory/2026-03-29.md
- memory/active-state.md
- AGENTS.md
- MEMORY.md

## [RUN-20260329-002] required-discord-main-completion-ping-was-missed-because-task-cl

**Logged**: 2026-03-29T16:00:00-04:00
**Summary**: Required Discord main-completion ping was missed because task closeout had no notification gate
**Branch**: repair-pattern
**Signal Kind**: request-friction
**Area**: workflow
**Priority**: high
**Status**: accepted
**Source**: user_feedback

### Full Problem
A qualifying main-task completion happened without the required Discord update, even though the route and config were active. The failure was not transport; it was workflow. The existing rule said to send the ping, but task closeout still allowed completion to be declared without explicitly resolving notification applicability.

### Context
The main completion-update feature created yesterday remained enabled and pointed at #main_updates with #control-center fallback. The miss happened because the rule lived as a standalone obligation instead of a closeout decision point.

### Root Cause
The protocol was advisory rather than gating: a direct task could still be treated as finished without explicitly resolving whether the required Discord completion update had been sent, was not applicable, or was blocked/deferred.

### Lessons Captured
- A side-effect required at task completion should not live as a floating reminder; it needs an explicit closeout gate.
- If a route/config is working but the action is omitted, repair the closeout workflow before touching transport.
- When an existing protocol fails, revise it into the real decision point instead of stacking another reminder beside it.

### Protocol Outcomes
- Revise the main-completion Discord rule into a closeout gate: do not treat a qualifying direct task as closed until one branch is resolved — ping sent, not applicable, or blocked/deferred with reason.
- Use scripts/main_task_closeout.py as the helper to resolve the branch and generate the notification line when the ping applies.

### Changes Made
Rewrote the AGENTS rule from a standalone completion ping into a closeout gate; added machine-readable closeout-gate fields to mission-control/data/notifications.json; revised the protocol registry entry; added scripts/main_task_closeout.py; updated TOOLS.md, MEMORY.md, active-state, and the archived task note to reflect the new workflow.

### Validation
Ran an outside-review diagnosis, validated the updated JSON files, compiled scripts/main_task_closeout.py successfully, and tested both the ping-sent and deferred branches so the helper now emits the expected closeout output.

### Related Files
- mission-control/data/tasks.json
- memory/2026-03-29.md
- .learnings/PROTOCOLS.md

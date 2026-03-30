# Branch importance rubric

Use this rubric for long-lived agent/channel identities when deciding what is important enough to keep, escalate, or promote into shared memory.

## Shared-important (should move upward)

Treat an item as **shared-important** when it affects any of these:

- safety, access, permissions, safeguards, or boundaries
- user commitments, deadlines, schedules, reminders, or promised follow-up
- shared project state, active tasks, durable decisions, or operating rules
- blockers, failures, repeated friction, or incidents that may require repair
- meaningful actions by subordinate agents that a supervisor should know about
- anything likely to matter after a restart or outside the current chat transcript

These should be escalated upward through the hierarchy:
- subordinate Discord agents -> Discord control-channel agent
- Discord control-channel agent -> main

## Branch-important but local

Treat an item as **branch-important but local** when it matters inside that branch/agent, but does not yet need promotion into main memory.

Examples:
- local sandbox state for a safeguarded guest agent
- branch-local housekeeping
- temporary context needed for the next wake within that branch

Keep these in the local state file for that agent/branch.

## Not important enough to retain

Do **not** escalate or preserve routine low-value chatter such as:

- casual banter
- acknowledgements / thanks / reaction-only messages
- tiny routine actions with no follow-up consequence
- observations that are easy to re-derive and have no lasting effect

## Role-specific application

### Main
Main decides what becomes shared durable memory for the overall facility.

### Discord control-channel agent
Promote upward when:
- the control branch did something important
- a subordinate reported something shared-important
- a branch-level issue could affect main priorities, safety, or project continuity

### Guest safe-web sandbox
Report upward to the control-channel agent only when:
- sandbox-management, safety, or boundary issues arise
- a meaningful branch-level escalation is needed

Keep routine sandbox exploration and local state separate.

## Maintenance-worker responsibility

The hourly maintenance worker should audit pending branch-important items recorded in the agent-namecard state files and:

1. promote unresolved shared-important items into main memory/task state when appropriate
2. leave branch-local-only items in their local state
3. stamp review metadata so the same item is not treated as unseen forever

This worker is an auditor/promoter, not the original judge of importance. The branch agent or sub-head should still make the first importance call at capture time.

# 2026-04-02 repair run — Discord closeout over-hardening caused token burn

## Signal
- Repeated friction / operational failure.
- Haolun reported that model usage ran out and suspected always-on high thinking across agents.
- A one-hour token audit then showed the real dominant sink was the standing `recover-main-task-closeouts` worker.

## Observed symptoms
- Window: 2026-04-02 10:47–11:52 EDT.
- Session-store delta: `228,539` total tokens.
- `recover-main-task-closeouts` alone consumed about `181,074` total tokens across 13 runs (~79% of the measured total).
- The worker usually woke to discover there was nothing to send.

## Root cause
The completion-ping workflow had been repaired for restart durability without enough proportionality to the actual importance of the ping. The system treated a missed Discord completion ping as if it were high-value enough to justify a standing recovery poller, durable queue semantics, and a task-closeout gate. In reality, haolun considers a missed ping acceptable because the finished task will usually be visible anyway.

## Generalized moral
Do not build persistent recovery loops for low-stakes notifications. Match reliability machinery to the real importance of the signal. For low-cost / low-consequence pings, prefer one-shot best-effort delivery plus lightweight local logging over standing pollers and restart-recovery infrastructure.

## Branch
- `repair-pattern`

## Failed / repaired layer
- Workflow + notification delivery protocol.
- The earlier protection was not unsafe, but it was overbuilt and operationally expensive relative to the value it protected.

## Smallest safe change chosen
- Remove the standing `recover-main-task-closeouts` cron job.
- Rewrite `scripts/main_task_closeout.py` from durable queue/recovery semantics into a best-effort one-shot announce helper with a local ledger.
- Update AGENTS/MEMORY/active-state/TOOLS/protocol/notifications so task closure no longer waits on delivery success.
- Keep the notification format and target channel intact.

## Validation
- Took a reversible snapshot before editing via `skills/grounded-evolver/scripts/snapshot_revert.py`.
- Recompiled the rewritten helper successfully.
- Ran a dry-run preview of the helper and confirmed it generated the expected one-line ping payload and ledger write shape.
- Removed the recurring recovery cron and confirmed the cron list now contains only `maintain-workspace-hourly`.

## Durable artifacts updated
- `AGENTS.md`
- `MEMORY.md`
- `memory/active-state.md`
- `TOOLS.md`
- `mission-control/data/notifications.json`
- `mission-control/data/protocol.json`
- `mission-control/data/main-task-closeouts.json`
- `scripts/main_task_closeout.py`
- `memory/2026-04-02.md`
- `mission-control/data/tasks.json`

## Remaining follow-up
- The hourly maintenance worker is still the next biggest recurring sink and should be tuned separately.

## [RUN-20260402-001] github-push-protection-blocked-workspace-sync-because-a-secret-b

**Logged**: 2026-04-02T18:30:15-04:00
**Summary**: GitHub push protection blocked workspace sync because a secret-bearing backup snapshot entered git history
**Branch**: build-pattern
**Signal Kind**: blocker
**Area**: infra
**Priority**: high
**Status**: accepted
**Source**: tool_failure

### Full Problem
Hourly workspace sync looked like an auth/network issue, but a manual push surfaced GitHub GH013 push protection. A backup snapshot under .learnings/snapshots contained a Discord bot token, so origin/main rejected the pushed local commit range.

### Context
No extra context recorded.

### Root Cause
A config backup file with live secrets was allowed into tracked git history, and scripts/git-auto-sync.sh suppressed push stderr so the true blocker was hidden.

### Lessons Captured
- Do not allow secret-bearing backup snapshots into tracked git history; ignore them before they can be auto-committed.
- When automated git sync fails, preserve a trimmed version of fetch/push stderr so auth problems can be distinguished from push-protection or policy failures.

### Protocol Outcomes
- Keep .learnings/snapshots/*.bak ignored because backup snapshots may contain secrets even when the paired .json path is ignored.
- If git auto-sync reports push_failed, inspect the emitted detail text before assuming SSH/auth is broken.

### Changes Made
Rewrote the 4 local commits ahead of origin/main to remove the secret-bearing .bak file from history, added .learnings/snapshots/*.bak to .gitignore, pushed the cleaned branch successfully, and updated scripts/git-auto-sync.sh + TOOLS.md with the new guardrails.

### Validation
git push --dry-run origin main succeeded after the rewrite, the real push to origin/main succeeded, the secret-bearing path no longer appears in git history, and auto-sync now preserves a trimmed detail string on fetch/push failure.

### Related Files
- .learnings/snapshots/openclaw.json.main-token-efficiency-pass-2026-04-02.bak
- scripts/git-auto-sync.sh

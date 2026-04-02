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

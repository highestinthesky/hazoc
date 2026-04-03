# Protocol Outcomes

Protocol candidates, revisions, and accepted guardrails discovered through learning runs.
Accepted protocols still need promotion into their canonical operating files and indexing in `mission-control/data/protocol.json`.

## [PRT-20260329-001] learning-run-artifact-pack

**Logged**: 2026-03-29T15:42:00-04:00
**Status**: accepted
**Area**: learning-system
**Source Run**: user-request-20260329-learning-artifacts

### Protocol Outcomes
- Finish every completed learning run with three durable artifacts: full problem detail in the day's `.learnings/.../error.md`, a succinct summary in `memory/YYYY-MM-DD.md`, and distilled lesson/protocol outcomes in `.learnings/`.
- If a protocol becomes accepted, also promote it into its canonical operating file and keep the protocol registry in sync.
- Treat the learning run as incomplete if those artifacts do not exist yet.

### Canonical Homes
- AGENTS.md
- MEMORY.md
- skills/learning-loop/SKILL.md
- skills/learning-loop/references/request-friction-protocol.md
- mission-control/data/protocol.json

### Why
A learning-system trigger should leave behind a durable, inspectable trail instead of depending on chat memory or good intentions.

---

## [PRT-20260329-002] stale-reset-anchor-expectation-was-surfaced-as-live-state-after-

**Logged**: 2026-03-29T15:45:00-04:00
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260329-001

### Protocol Outcomes
- Treat expected-next-step bullets as unconfirmed until newer state or the current conversation corroborates them.
- Keep memory/active-state.md live-only; move archival handoff prose to daily notes instead.

### Canonical Homes
- AGENTS.md
- memory/active-state.md
- MEMORY.md

### Why
Live anchor state and historical predicted-next-step notes were mixed together, and the maintenance protocol lacked an explicit freshness/supersession check for future-looking handoff bullets.

---

## [PRT-20260329-003] required-discord-main-completion-ping-was-missed-because-task-cl

**Logged**: 2026-03-29T16:00:00-04:00
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260329-002

### Protocol Outcomes
- Revise the main-completion Discord rule into a closeout gate: do not treat a qualifying direct task as closed until one branch is resolved — ping sent, not applicable, or blocked/deferred with reason.
- Use scripts/main_task_closeout.py as the helper to resolve the branch and generate the notification line when the ping applies.

### Canonical Homes
- AGENTS.md
- mission-control/data/notifications.json
- mission-control/data/protocol.json
- TOOLS.md
- scripts/main_task_closeout.py
- MEMORY.md
- memory/active-state.md

### Why
The protocol was advisory rather than gating: a direct task could still be treated as finished without explicitly resolving whether the required Discord completion update had been sent, was not applicable, or was blocked/deferred.

---

## [PRT-20260329-004] discord-completion-closeout-needed-a-durable-queue-and-restart-s

**Logged**: 2026-03-29T17:47:00-04:00
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260329-003

### Protocol Outcomes
- For qualifying main-task completions, queue the Discord ping durably before task closure, then hand it off through an immediate isolated announce job and keep a persistent recovery cron draining the queue after restarts.
- Use mission-control/data/main-task-closeouts.json as the durable queue and scripts/main_task_closeout.py as the single closeout helper for queueing, dispatching, and recovery.

### Canonical Homes
- AGENTS.md
- mission-control/data/notifications.json
- mission-control/data/protocol.json
- mission-control/data/main-task-closeouts.json
- TOOLS.md
- MEMORY.md
- memory/active-state.md
- scripts/main_task_closeout.py

### Why
The existing protocol guarded intent, not the delivery handoff. It lacked durable pending-state plus restart-safe recovery, so a restart or simple omission could still drop the notification even though the rule existed.

---

## [PRT-20260402-001] low-stakes-completion-pings-should-not-justify-standing-recovery-pollers

**Logged**: 2026-04-02T13:36:00-04:00
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260402-001

### Protocol Outcomes
- Replace the durable closeout gate for direct main-task Discord pings with a single best-effort completion ping.
- Use `scripts/main_task_closeout.py` to append a local ledger entry and enqueue one lightweight one-shot announce job.
- Do not block task closure on delivery success and do not keep a standing recovery worker for missed pings.

### Canonical Homes
- AGENTS.md
- mission-control/data/notifications.json
- mission-control/data/protocol.json
- TOOLS.md
- MEMORY.md
- memory/active-state.md
- scripts/main_task_closeout.py
- mission-control/data/main-task-closeouts.json

### Why
The prior repair overfit reliability to a low-stakes signal. The standing recovery cron spent far more tokens checking for missed pings than the missed pings were worth.

---

## [PRT-20260402-002] github-push-protection-blocked-workspace-sync-because-a-secret-b

**Logged**: 2026-04-02T18:30:15-04:00
**Status**: accepted
**Area**: infra
**Source Run**: RUN-20260402-001

### Protocol Outcomes
- Keep .learnings/snapshots/*.bak ignored because backup snapshots may contain secrets even when the paired .json path is ignored.
- If git auto-sync reports push_failed, inspect the emitted detail text before assuming SSH/auth is broken.

### Canonical Homes
- .gitignore
- TOOLS.md
- scripts/git-auto-sync.sh

### Why
A config backup file with live secrets was allowed into tracked git history, and scripts/git-auto-sync.sh suppressed push stderr so the true blocker was hidden.

---

## [PRT-20260402-003] learning-layout-was-misleading-current-error-details-landed-unde

**Logged**: 2026-04-02T19:36:29-04:00
**Status**: accepted
**Area**: memory
**Source Run**: RUN-20260402-001

### Protocol Outcomes
- When reading or routing learning/error history, start from .learnings/errors/ and ERROR_INDEX.md; only open .learnings/days/ if date-local archive context is needed.

### Canonical Homes
- .learnings/README.md
- .learnings/ERROR_INDEX.md
- .learnings/errors
- skills/learning-loop/scripts/log_learning_run.py
- skills/learning-loop/scripts/normalize_learning_layout.py
- skills/learning-loop/scripts/check_learning_layout.py

### Why
Capture/archive surfaces, canonical readable error history, and index/docs were not sharply separated, so writes and reads drifted into different places.

---

## [PRT-20260402-004] learning-layout-drift-and-closeout-ledger-ambiguity-obscured-the

**Logged**: 2026-04-02T20:36:49-04:00
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260402-002

### Protocol Outcomes
- Canonical readable learning errors live in `.learnings/errors/YYYY-MM.md`; `.learnings/days/YYYY-MM-DD/error.md` is archive-pointer/day-local context only.
- When a recent completion ping looks missing, verify cron run history plus the local closeout ledger before redesigning the notification architecture.

### Canonical Homes
- skills/learning-loop/SKILL.md
- skills/learning-loop/references/promotion-map.md
- skills/learning-loop/references/request-friction-protocol.md
- scripts/main_task_closeout.py
- mission-control/data/notifications.json

### Why
The canonical/archive boundary in the learning layout was only partially enforced across scripts, docs, and existing files, so old structure leaked back into current retrieval. Separately, the closeout ledger recorded enqueue state but did not automatically reconcile historical deliveries, which made a healthy transport path look suspect. The helper also used a shared temporary filename for ledger writes, which made concurrent/manual reconciliation fragile.

---

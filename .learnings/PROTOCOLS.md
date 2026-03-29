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

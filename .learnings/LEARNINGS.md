# Learnings

Raw lessons, corrections, and best practices that are not yet promoted.

## [LRN-20260324-001] gogcli-under-wsl-headless-may-need-file-keyring-

**Logged**: 2026-03-24T09:47:50-04:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
gogcli under WSL/headless may need file keyring + local password wrapper

### Details
Without a usable desktop keychain, gog auth token storage failed in WSL with 'no TTY available for keyring file backend password prompt'. A local password file plus wrapper exporting GOG_KEYRING_PASSWORD allowed the file backend to work.

### Suggested Action
If gog auth fails under WSL/headless, switch to file keyring and ensure GOG_KEYRING_PASSWORD is set non-interactively before exchanging the OAuth callback.

### Metadata
- Source: tool_failure
- Related Files: none
- Tags: gog, gogcli, wsl, oauth, keyring
- See Also: none

---

## [LRN-20260328-001] keep-skill-source-in-skills-and-generated-skill-

**Logged**: 2026-03-28T10:38:07-04:00
**Priority**: medium
**Status**: pending
**Area**: git

### Summary
Keep skill source in skills/ and generated .skill bundles in ignored dist/

### Details
The editable source of custom skills should live under skills/<name>/. Packaged .skill archives are generated artifacts and should be written to the ignored dist/ directory rather than tracked at the repo root. Root-level packaged duplicates created confusion during git review because they looked like standalone source files even though they matched the skill folders byte-for-byte.

### Suggested Action
When packaging local skills, write exports to dist/ and avoid tracking root-level .skill files unless there is a specific release/distribution reason.

### Metadata
- Source: workflow_observation
- Related Files: none
- Tags: git, skills, packaging, repo-layout
- See Also: none

---

## [LRN-20260329-001] stale-reset-anchor-expectation-was-surfaced-as-live-state-after-

**Logged**: 2026-03-29T15:45:00-04:00
**Priority**: high
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260329-001

### Summary
Stale reset-anchor expectation was surfaced as live state after the step had already happened

### Lessons
- Distinguish confirmed current state from historical predicted next steps during reset anchors.
- If a file is treated as a live anchor, keep archival handoff prose out of it.
- Maintenance protocols must audit stale predictions, not just stale objects.

### Promotion Notes
Canonical protocol paths: AGENTS.md, memory/active-state.md, MEMORY.md

---

## [LRN-20260329-002] required-discord-main-completion-ping-was-missed-because-task-cl

**Logged**: 2026-03-29T16:00:00-04:00
**Priority**: high
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260329-002

### Summary
Required Discord main-completion ping was missed because task closeout had no notification gate

### Lessons
- A side-effect required at task completion should not live as a floating reminder; it needs an explicit closeout gate.
- If a route/config is working but the action is omitted, repair the closeout workflow before touching transport.
- When an existing protocol fails, revise it into the real decision point instead of stacking another reminder beside it.

### Promotion Notes
Canonical protocol paths: AGENTS.md, mission-control/data/notifications.json, mission-control/data/protocol.json, TOOLS.md, scripts/main_task_closeout.py, MEMORY.md, memory/active-state.md

---

## [LRN-20260329-003] discord-completion-closeout-needed-a-durable-queue-and-restart-s

**Logged**: 2026-03-29T17:47:00-04:00
**Priority**: high
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260329-003

### Summary
Discord completion closeout needed a durable queue and restart-safe recovery, not just a rule/helper

### Lessons
- Do not call an external-notification closeout reliable unless the handoff is durably recorded and recoverable after restart.
- When a helper remains advisory and session-bound, the real failed layer is workflow plus delivery handoff, not memory wording.
- A persistent queue plus idempotent dispatcher is a better repair than stacking more checklist language on top of a false gate.

### Promotion Notes
Canonical protocol paths: AGENTS.md, mission-control/data/notifications.json, mission-control/data/protocol.json, mission-control/data/main-task-closeouts.json, TOOLS.md, MEMORY.md, memory/active-state.md, scripts/main_task_closeout.py

---

## 2026-04-02 — reliability should be proportional to notification importance

**Area**: workflow
**Source Run**: RUN-20260402-001

### Summary
Low-stakes Discord completion pings should not use a standing recovery poller; a one-shot best-effort send plus lightweight local logging is the better fit.

### Lessons
- Do not build persistent recovery loops for low-stakes notifications.
- Match reliability machinery to the real cost of a miss, not to abstract discomfort about imperfection.
- When a safety/reliability layer becomes the dominant ongoing cost, revisit whether the protected signal is important enough to justify it.

### Promotion Notes
Canonical protocol paths: AGENTS.md, mission-control/data/notifications.json, mission-control/data/protocol.json, mission-control/data/main-task-closeouts.json, TOOLS.md, MEMORY.md, memory/active-state.md, scripts/main_task_closeout.py

---

## [LRN-20260402-001] openclaw-cron-add-rejected-at-5s

**Logged**: 2026-04-02T15:06:05-04:00
**Priority**: medium
**Status**: pending
**Area**: tooling

### Summary
OpenClaw cron add rejected --at +5s

### Details
On OpenClaw 2026.3.28, the closeout helper failed with 'Invalid --at; use ISO time or duration like 20m' when it passed '--at +5s'. Switching to the bare duration '5s' succeeded.

### Suggested Action
For one-shot cron jobs on this runtime, use bare durations like 5s/20m instead of +5s until the parser behavior changes.

### Metadata
- Source: self_observation
- Related Files: none
- Tags: openclaw, cron, closeout
- See Also: none

---

## [LRN-20260402-002] github-push-protection-blocked-workspace-sync-because-a-secret-b

**Logged**: 2026-04-02T18:30:15-04:00
**Priority**: high
**Status**: accepted
**Area**: infra
**Source Run**: RUN-20260402-001

### Summary
GitHub push protection blocked workspace sync because a secret-bearing backup snapshot entered git history

### Lessons
- Do not allow secret-bearing backup snapshots into tracked git history; ignore them before they can be auto-committed.
- When automated git sync fails, preserve a trimmed version of fetch/push stderr so auth problems can be distinguished from push-protection or policy failures.

### Promotion Notes
Canonical protocol paths: .gitignore, TOOLS.md, scripts/git-auto-sync.sh

---

## [LRN-20260402-003] learning-layout-was-misleading-current-error-details-landed-unde

**Logged**: 2026-04-02T19:36:29-04:00
**Priority**: high
**Status**: accepted
**Area**: memory
**Source Run**: RUN-20260402-001

### Summary
Learning layout was misleading: current error details landed under .learnings/days even though the readable error corpus should live under .learnings/errors

### Lessons
- Keep one canonical home for readable error history (.learnings/errors/YYYY-MM.md) and treat .learnings/days/ as archive-only raw context.
- Avoid root file/directory name collisions like errors.md vs errors/ when humans are expected to scan the tree quickly.

### Promotion Notes
Canonical protocol paths: .learnings/README.md, .learnings/ERROR_INDEX.md, .learnings/errors, skills/learning-loop/scripts/log_learning_run.py, skills/learning-loop/scripts/normalize_learning_layout.py, skills/learning-loop/scripts/check_learning_layout.py

---

## [LRN-20260402-004] learning-layout-drift-and-closeout-ledger-ambiguity-obscured-the

**Logged**: 2026-04-02T20:36:49-04:00
**Priority**: high
**Status**: accepted
**Area**: workflow
**Source Run**: RUN-20260402-002

### Summary
Learning layout drift and closeout ledger ambiguity obscured the real state of errors and pings

### Lessons
- Keep one canonical readable error ledger and make archive day files point back to it instead of competing with it.
- For best-effort completion pings, check actual cron run history before assuming delivery failed or rebuilding heavy recovery machinery.
- Local JSON ledgers that may be updated concurrently should use unique temp-file names when writing.

### Promotion Notes
Canonical protocol paths: skills/learning-loop/SKILL.md, skills/learning-loop/references/promotion-map.md, skills/learning-loop/references/request-friction-protocol.md, scripts/main_task_closeout.py, mission-control/data/notifications.json

---

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

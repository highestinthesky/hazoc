# Errors

Repeatable failures, broken commands, and debugging notes worth remembering.

## [ERR-20260324-001] don-t-misread-gog-as-gog-com-when-user-reference

**Logged**: 2026-03-24T09:47:50-04:00
**Priority**: high
**Status**: pending
**Area**: tools

### Summary
Don't misread 'gog' as GOG.com when user references the ClawHub skill

### Error
I initially installed Heroic Games Launcher because I interpreted 'gog' as Good Old Games, but the user meant the ClawHub skill steipete/gog for Google Workspace.

### Context
No extra context recorded.

### Suggested Fix
When 'gog' appears in OpenClaw/ClawHub context, check for the skill URL/slug first before assuming the gaming launcher.

### Metadata
- Source: user_feedback
- Related Files: none
- Tags: gog, clawhub, misunderstanding
- See Also: none

---

## [ERR-20260324-002] recurring-github-push-duty-was-recorded-but-not-

**Logged**: 2026-03-24T20:44:49-04:00
**Priority**: high
**Status**: pending
**Area**: workflow

### Summary
Recurring GitHub push duty was recorded but not actually executed

### Error
Mission-control showed the recurring GitHub push task, but git history still matched origin/main and recent workspace changes were uncommitted. The reminder existed without an actual commit/push check.

### Context
No extra context recorded.

### Suggested Fix
When active work is happening, verify git status/log explicitly, make a local commit for meaningful changes, and only treat the duty as done after a real push (with user approval for the external step).

### Metadata
- Source: user_feedback
- Related Files: none
- Tags: github, git, recurring-duties, mission-control
- See Also: none

---

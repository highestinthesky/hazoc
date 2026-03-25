# Algorithm

## Phase 1 — Signal intake

Start from something real:
- request
- blocker
- correction
- repeat failure
- drift
- decision
- progress worth preserving

Write the signal in one sentence.

## Phase 2 — Classify

Classify along these axes:

- **impact**: how much the issue matters
- **loss risk**: how easy it is to lose this context
- **repeat count**: how often it has happened
- **structure need**: whether relations matter more than prose
- **blast radius**: how risky the possible change is

## Phase 3 — Choose mutation class

Recommended classes:
- memory capture
- task update
- daily-note update
- durable rule/preference promotion
- lesson logging
- graph augmentation
- workflow/skill patch

Prefer lower blast radius classes first.

## Phase 4 — Validate

Pick one concrete proof:
- context survives a gap/restart
- task detail is clearer
- failure does not repeat
- workflow shortens
- relation query becomes answerable

## Phase 5 — Record outcome

Always leave behind:
- what changed
- why
- how it was checked
- what should happen next

## Heuristic priority

A good simple heuristic is:

`priority = impact + loss_risk + min(repeat_count, 3) + cross_channel_bonus + project_bonus + structure_bonus - blast_radius`

This is not magic. It just prevents underreacting to repeated important issues and overreacting to flashy but low-value ones.

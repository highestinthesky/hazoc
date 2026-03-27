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

## Phase 2 — Generalize the root cause

Before mutating, force one layer of abstraction.
Ask:
- What was the root cause?
- What broader failure mode does this belong to?
- What guideline would help future-you avoid this class of mistake on unrelated tasks?
- Is that guideline broad enough to transfer, but concrete enough to change behavior?

Do not stop at an incident-specific fix when a reusable moral is available.

## Phase 3 — Classify

Classify along these axes:

- **impact**: how much the issue matters
- **loss risk**: how easy it is to lose this context
- **repeat count**: how often it has happened
- **structure need**: whether relations matter more than prose
- **blast radius**: how risky the possible change is

## Phase 4 — Choose mutation class

Recommended classes:
- memory capture
- task update
- daily-note update
- durable rule/preference promotion
- lesson logging
- graph augmentation
- workflow/skill patch

Prefer lower blast radius classes first.

## Phase 5 — Validate

Pick one concrete proof:
- context survives a gap/restart
- task detail is clearer
- failure does not repeat
- workflow shortens
- relation query becomes answerable

Also verify that the chosen fix actually follows the generalized moral from Phase 2.
If it solves the local incident but violates the moral, the evolution is incomplete.

For UI-related work, do not stop at visual polish.
Also verify:
- the layout has no obvious display bugs in the real view/state
- the interaction actually works end to end
- the control's behavior matches its visual implication
- accidental destructive state changes are not too easy

## Phase 6 — Record outcome

Always leave behind:
- what changed
- why
- how it was checked
- what should happen next

## Heuristic priority

A good simple heuristic is:

`priority = impact + loss_risk + min(repeat_count, 3) + cross_channel_bonus + project_bonus + structure_bonus - blast_radius`

This is not magic. It just prevents underreacting to repeated important issues and overreacting to flashy but low-value ones.

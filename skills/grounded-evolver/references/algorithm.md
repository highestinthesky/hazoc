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

## Phase 1a — Choose the learning branch

Every signal must take **exactly one** of two branches.
There is no third peer `general-evolution` branch.

Keep **signal kind** separate from **branch**:
- signal kind = what type of signal this is (`request-friction`, `progress`, `decision`, `blocker`, `correction`, `cross-channel`, etc.)
- branch = whether the current pattern is being built/extended or repaired

### Branch 1 — `build-pattern`

Use when there is **no known failed or clearly insufficient protection yet**.
This includes:
- progress worth preserving
- decisions that should become durable state
- first-pass blockers/corrections/friction
- first-time request-friction
- new state that should be captured before it drifts away

### Branch 2 — `repair-pattern`

Use when the current pattern/protection is **already known to be insufficient**.
Trigger when either is true:
- an existing protocol/protection failed
- a followed protocol appears to have caused or amplified the problem
- undesirable friction repeated strongly enough to prove the current pattern is insufficient

This includes:
- failed existing protocol
- repeat failure
- repeated undesirable request-friction
- recurring skipped step / correction / workflow miss

### Protocol-causation question inside both branches

For problem/failure signals in either branch, explicitly ask:
- could this problem have been caused or amplified by one of the protocols currently being followed?

If the answer is yes:
- identify the specific protocol, rule, or checklist pattern if possible
- explain how it caused or amplified the problem
- prefer revising, narrowing, or removing that causal protocol instead of stacking another protocol on top
- if the evidence is strong enough, treat this as a `repair-pattern` case even if it first looked like a `build-pattern` case

### Request-friction inside the universal model

A **request-friction** signal means:
- a meaningful request occurred
- and there is evidence of friction, failure, a skipped step, repeat friction, or protocol weakness

Typical request-friction indicators:
- user correction
- tool failure
- skipped step
- protocol existed / protocol failed
- avoidable detour
- bad local fix
- repeat friction

### Packet guidance

If the signal is `request-friction`, capture at minimum:
- signal_kind
- request_context
- symptom_type
- impact
- repeat_count
- protection_state
- loss_risk
- blast_radius

If the signal is other undesirable friction, capture:
- signal_kind
- context
- failure_mode
- impact
- repeat_count
- protection_state
- loss_risk
- blast_radius

If the signal is constructive/neutral (for example progress or decisions), capture:
- signal_kind
- context
- outcome_type
- impact
- repeat_count
- protection_state
- loss_risk
- blast_radius

Optional fields when relevant:
- protection_reference
- observed_signals
- failed_layer

### Operational artifacts

The planner should not stop at branch classification.
For each signal, generate the artifacts needed to execute the branch:

- a structured problem/signal packet
- a self-authored prompt for the first pass
- an outside-review prompt when outside review is required
- a clean-room subagent spawn plan when outside review is required
- an artifact checklist showing what the run should leave behind

Use these artifacts to make the branch operational rather than leaving it as a conceptual diagram.

### Clean-room outside review rule

When outside review is required:
- use the generated `outside_review_prompt` as the **exact** subagent task
- do not rewrite it from memory
- do not attach extra files or parent-chat summaries
- prefer a sterile temp `cwd` outside the workspace
- treat the packet as the only allowed problem context

Important: this creates a best-effort clean room. If OpenClaw injects startup anchoring or other platform-level context into brand-new subagents, that behavior cannot be fully disabled from grounded-evolver alone; the prompt should explicitly instruct the reviewer to ignore any ambient context and rely only on the packet.

### Reversible protocol-mutation rule

When the planned mutation changes a protocol, rule, workflow, or skill behavior:
- capture the exact pre-change text before editing
- prefer surgical edits over whole-file overwrite so rollback is precise
- record the exact inserted block for new additions
- keep a revert plan before the mutation is accepted
- if vetting or post-change validation fails, restore the prior state immediately instead of leaving the mutation half-active

A good planner run should emit:
- whether revert handling is required
- a revert plan with pre-change capture steps
- rollback actions tied to the mutation surface

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

# Request-Friction Logging Handoff

Grounded-evolver now owns the branch logic.
This file is **not** a separate peer learning engine anymore.

Use it only after grounded-evolver has already classified the signal into one of its two universal branches:

- `build-pattern`
- `repair-pattern`

Signal kind remains separate.
`request-friction` is one signal kind inside grounded-evolver, not its own top-level evolution framework.

## Ownership split

### Grounded-evolver owns

- signal intake
- signal-kind classification
- branch choice (`build-pattern` vs `repair-pattern`)
- root-cause extraction
- generalized moral
- mutation-target selection
- validation planning
- deciding whether deeper workflow/skill/code repair is needed

See:
- `skills/grounded-evolver/SKILL.md`
- `skills/grounded-evolver/references/algorithm.md`
- `skills/grounded-evolver/scripts/grounded_evolve.py`

### Learning-loop owns

- durable logging
- promotion to the right memory layer
- `.learnings/` entry creation
- keeping the result from disappearing into chat

## When to use this handoff

Use this file when:
- grounded-evolver identified the signal kind as `request-friction`
- and you now need to persist the outcome cleanly

A `request-friction` signal means:
- a meaningful request occurred
- and there was evidence of friction, failure, a skipped step, repeat friction, or protocol weakness

Common indicators:
- user correction
- tool failure
- skipped step
- protocol existed / protocol failed
- avoidable detour
- bad local fix
- repeat friction

## Handoff flow

1. Run grounded-evolver first.
2. Read the resulting branch, problem packet, self-authored prompt, outside-review prompt (when present), clean-room spawn plan (when present), actions, and validation checks.
3. Carry out the branch-specific work.
4. Use learning-loop to store the result in the smallest correct home.
5. Report what changed.

## What to persist from grounded-evolver

Capture, at minimum:
- signal kind
- chosen branch
- problem packet
- protocol-causation assessment
- root cause
- generalized moral
- chosen mutation target
- what changed
- how it was validated
- what should happen next

## Branch-specific logging guidance

### If grounded-evolver chose `build-pattern`

Typical persistence shape:
- daily note entry for the incident
- `.learnings/LEARNINGS.md` if the lesson is still raw or unresolved
- `AGENTS.md` only if the prevention rule is already stable and clearly reusable

Good fit:
- first-time request friction
- first-pass correction where no prior protection failed
- a new prevention rule that still needs observation

### If grounded-evolver chose `repair-pattern`

Typical persistence shape:
- daily note entry for the failure and repair
- `.learnings/errors.md` + `.learnings/errors/YYYY-MM.md` for repeatable failures / failed protections
- `AGENTS.md`, `TOOLS.md`, or grounded-evolver/skill docs when the repaired rule/workflow is stable
- mission-control task memory if implementation work is still open

Good fit:
- failed existing protocol
- repeated request-friction
- deeper workflow/skill/code repair prompted by recurring failure

## Destination map

Route outputs to the smallest correct home:

- `memory/YYYY-MM-DD.md` -> raw incident note, context, what happened today
- `.learnings/errors.md` / `.learnings/errors/YYYY-MM.md` -> reproducible failures, broken workflows, failed protections
- `.learnings/LEARNINGS.md` -> not-yet-promoted lessons and recurring patterns
- `AGENTS.md` -> durable global operating rules
- `TOOLS.md` -> tool or environment-specific fixes
- grounded-evolver / skill docs -> stable workflow logic
- `mission-control/data/protocol.json` -> registry/index of accepted active protocols, each pointing to its canonical home
- mission-control task board -> project work, implementation tasks, follow-ups

## Standard artifacts

A good request-friction run should usually leave behind:

1. grounded-evolver plan output
2. chosen branch
3. durable write(s) in the right destination
4. explicit note of what changed and why
5. next step, if any remains

## Boundary conditions

- Do not redefine branch semantics here; grounded-evolver is the source of truth.
- Do not silently integrate risky changes.
- Keep sub-agent inputs scoped and sanitized when outside review is used.
- When outside review is used, send the generated `outside_review_prompt` as the exact subagent task instead of paraphrasing it.
- If a protocol/rule/workflow mutation is provisional, capture the exact pre-change text and be ready to revert it immediately if vetting or validation fails.
- Prefer the smallest durable write that preserves the lesson.

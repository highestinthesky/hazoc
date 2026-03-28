# Request Friction Protocol

Use this when improving the learning process itself, or when a request revealed friction, failure, or a workflow miss.

## Trigger

Run a quick friction check after each meaningful request:

- Did anything go wrong?
- Was there avoidable friction?
- Did a protocol fail, get skipped, or prove insufficient?

If **no**, end this protocol and continue normal memory optimization.

If **yes**, choose the branch below.

## Branch A — first-time or not-yet-recurring problem

Use this when the problem does **not** appear to be a repeat failure of an existing protocol.

### 1) Record the problem set

Capture, at minimum:

- request / task context
- what went wrong or felt rough
- likely cause
- risk if repeated
- whether any existing protocol already covered it

### 2) Generate a self-authored prevention list

Write your own first pass at general rules or protocols that would have prevented this class of mistake.

Bias toward:

- generalizable rules, not one-off patches
- prevention, not just postmortems
- small durable changes first

### 3) Get a clean third-party take

Spawn an isolated sub-agent with **no current conversational baggage beyond the problem packet**.
Ask it to:

- review the problem set as if advising a third party
- generalize the pattern
- propose protocols that would prevent similar failures in the future

### 4) Combine and generalize

Combine the self-authored list and the third-party list.
Feed the combined draft back through a clean rewrite step with the explicit goal of making the protocols as general, reusable, and non-fragile as possible.

### 5) Revise once more yourself

Do one more human-facing pass yourself before promotion:

- remove overfitting
- tighten wording
- split mixed rules apart
- make the operational trigger obvious

### 6) Safety/security vet

Before integrating, ask:

- could this expand access unsafely?
- could this normalize risky autonomous behavior?
- could this write sensitive information into memory?
- could this cause future overreach or brittle behavior?

If risk is non-trivial or unclear, **stop** and present the proposed protocols plus risks to haolun instead of integrating them silently.

### 7) Merge with current protocol set

If safe, review existing protocols:

- if overlapping, expand or merge the existing rule rather than duplicating it
- if non-overlapping, add the new rule in the smallest correct home

### 8) Save + report

Write the durable result to the correct destinations and tell haolun what changed.

## Branch B — repeated problem or protocol failure

Use this when the same problem happened again, or when an existing protocol clearly failed.

### 1) Review the existing protocol

Look up the already-written protocol, rule, or workflow that was supposed to prevent the issue.
Then record:

- which protocol existed
- how reality diverged from it
- why it failed (ambiguity, missing trigger, too weak, not implemented, etc.)

### 2) Record the failure explicitly

Log:

- the error / friction
- the failed protocol(s)
- your own diagnosis of why the protection failed

### 3) Get a clean outside diagnosis

Spawn an isolated sub-agent with only the failure packet.
Ask it to explain:

- why the system still failed
- what the root issue seems to be
- what class of fix is required

### 4) Produce two change plans

Create:

- a **self-generated change plan** for fixing the failure
- a **third-party suggested change plan** from the clean sub-agent

Do **not** limit either plan to light protocol rewording if the failure points to a deeper implementation or workflow gap.
It is valid to propose system, tooling, or code changes when the protocol itself is not enough.

### 5) Combine into finalized revisions

Merge the two plans into one revised set of changes.
Prefer:

- smallest change that actually fixes the class of failure
- durable implementation over cosmetic wording
- explicit triggers and validation steps

### 6) Safety/security vet

Vet the proposed revisions before applying them.
If risky or unclear, **stop** and present the suggested changes plus risks to haolun.

### 7) Implement when safe

If safe:

- implement the approved revisions
- update the relevant protocol / skill / code / task memory
- save the learning into permanent memory
- report the new learning and the concrete change back to haolun

## Destination map

Route outputs to the smallest correct home:

- `memory/YYYY-MM-DD.md` → raw incident note, context, what happened today
- `.learnings/ERRORS.md` → reproducible failures, broken workflows, failed protocols
- `.learnings/LEARNINGS.md` → not-yet-promoted lessons and recurring patterns
- `AGENTS.md` → durable operating rules for hazoc
- `TOOLS.md` → tool or environment-specific fixes
- skill `SKILL.md` / references → workflow-specific operating logic
- mission-control task board → project work, implementation tasks, follow-ups

## Standard artifacts

When this protocol runs well, it should usually produce these artifacts:

1. problem packet
2. self-generated list or change plan
3. clean sub-agent take
4. combined draft
5. finalized vetted rule/change set
6. durable write(s) in the right home

## Boundary conditions

- Keep sub-agent inputs scoped and sanitized.
- Do not leak sensitive chat content unless needed.
- Do not silently integrate risky changes.
- Prefer general protocols for first-time issues.
- Escalate to deeper system/code changes when a repeated failure proves the protocol layer alone is insufficient.

# Lightweight agent bootstrap design

## Goal

Build the lightest practical agent/subagent identity system that still keeps behavior reliable.

Success means:
- one-shot helpers do not drag broad workspace memory into every run
- long-lived agents and recurring workers still have durable identity/state
- required rules stay explicitly conveyed
- the system does not rely on vague session memory
- the design matches OpenClaw's real lifecycle instead of pretending we can talk to a child before bootstrap

## Important runtime constraint

OpenClaw injects its fixed bootstrap context before a spawned child starts acting.
That means the right target is **minimal bootstrap + strong spawn packet discipline**, not "pre-bootstrap telepathy".

Practical consequence:
- we **can** choose what task packet the child receives at spawn time
- we **cannot** make a normal one-shot child be literally blank and wait for a later identity whisper before bootstrap

## Core design

Use a **three-layer identity model**:

1. **Long-lived agents** -> durable namecard + state bundle
2. **Recurring workers** -> durable worker spec + state bundle
3. **One-shot subagents** -> class spec compiled into a tiny spawn packet

The key split is:
- **durable actors read their own bundle**
- **disposable actors receive a compiled packet and read nothing else by default**

That keeps the system both light and robust.

## Recommended directory layout

```text
agent-namecards/
  index.json
  <card-id>/
    namecard.json
    state.json

workers/
  <worker-id>/
    spec.json
    state.json

subagent-classes/
  README.md
  index.json
  oneshot-reviewer.json
  oneshot-researcher.json
  oneshot-editor.json
  oneshot-verifier.json
  oneshot-summarizer.json
```

Do **not** merge everything into one giant directory just for neatness. The current split maps well to lifecycle:
- `agent-namecards/` = persistent identity
- `workers/` = scheduled/restart-sensitive identity
- `subagent-classes/` = disposable class templates

## Actor classes

### 1) Main / branch / persistent agents

Use for:
- main direct session
- long-lived branch agents
- channel-specific persistent identities

Source of truth:
- `agent-namecards/index.json`
- `agent-namecards/<card-id>/namecard.json`
- `agent-namecards/<card-id>/state.json`

Bootstrap rule:
- on startup or re-anchor, read the small identity bundle
- use local state by default
- only promote cross-agent information explicitly

Good fit:
- main
- Discord control branch
- any future long-lived specialist agent

### 2) Managed workers

Use for:
- hourly maintenance
- recovery dispatchers
- restart-sensitive recurring jobs

Source of truth:
- `workers/<worker-id>/spec.json`
- `workers/<worker-id>/state.json`

Bootstrap rule:
- every wake includes exact `worker-id` + bootstrap command
- worker reads its own spec/state before acting

Good fit:
- recurring cron jobs
- background recoveries
- durable queue processors

### 3) One-shot subagents

Use for:
- short review jobs
- narrow research
- verification
- small editing passes
- disposable analysis helpers

Source of truth:
- `subagent-classes/<class-id>.json`

Bootstrap rule:
- **parent reads the class spec, not the child**
- parent compiles a tiny task packet from the class spec + task-specific excerpts
- child receives the compiled packet at spawn time and should not read the registry by default

Good fit:
- almost all `sessions_spawn(mode="run", cleanup="delete")` helpers

## Why this is the most efficient model

Because a one-shot helper should not pay two costs:
1. reading a registry to figure out what it is
2. then reading task context to do the job

For disposable helpers, the parent already knows the class and the task.
So the efficient move is:
- parent resolves class
- parent attaches only the needed excerpts
- child works directly from the compiled packet

In other words:
- **class files are for the parent/orchestrator**
- **task packets are for the disposable child**

## One-shot class spec shape

Recommended minimal schema:

```json
{
  "classId": "oneshot-verifier",
  "kind": "oneshot",
  "purpose": "Check a proposed result against the provided packet only.",
  "spawnDefaults": {
    "thinking": "minimal",
    "mode": "run",
    "cleanup": "delete",
    "runTimeoutSeconds": 300
  },
  "contextPolicy": {
    "defaultMode": "minimal",
    "allowWorkspaceReads": false,
    "allowMemorySearch": false,
    "allowTaskBoardReads": false,
    "allowActiveStateReads": false,
    "allowProtocolReads": false,
    "maxAttachmentChars": 12000,
    "maxAttachments": 4
  },
  "packetRules": {
    "mustInclude": [
      "goal",
      "expectedOutput",
      "acceptanceChecks"
    ],
    "missingContextBehavior": "report-gap"
  },
  "outputContract": {
    "format": "bullets",
    "requiredSections": ["result", "evidence", "gaps", "risks"]
  },
  "guardrails": [
    "Treat the task packet and attachments as the only available context.",
    "Do not assume workspace-global memory.",
    "If key context is missing, report the gap instead of inventing it."
  ]
}
```

Notes:
- Use human-readable `classId`s, not raw numbers, as the canonical ids.
- If numeric aliases are desired, keep them in `subagent-classes/index.json`.

Example alias map:

```json
{
  "4": "oneshot-verifier",
  "5": "oneshot-reviewer"
}
```

## Spawn packet compiler

Extend `scripts/build_subagent_brief.py` or replace it with a new helper like:

```bash
python3 scripts/build_subagent_packet.py \
  --class-id oneshot-verifier \
  --goal "Check whether the proposed patch satisfies the request" \
  --expected-output "Short verdict with evidence and gaps" \
  --excerpt src/app.js:120:220 \
  --acceptance-check "Point out any unmet requirement" \
  --json
```

Compiler responsibilities:
- load the class spec
- merge class guardrails into the packet
- enforce attachment/context budgets
- reject disallowed broad context by default
- emit:
  - task packet text
  - attachments
  - spawn defaults (`thinking`, timeout, cleanup, mode)

## Parent-side spawn contract

Default rule for one-shot helpers:
- `mode: "run"`
- `cleanup: "delete"`
- low/minimal thinking unless the class says otherwise
- attach excerpts, not full files, unless explicitly justified
- do not tell the child to read `AGENTS.md`, `TOOLS.md`, `memory/active-state.md`, task board, or daily notes unless the job actually needs them

Parent widening policy:
- if the first packet is insufficient, the child should return a gap
- the **parent** decides whether to widen context and respawn or continue
- do not let disposable children self-escalate into broad workspace exploration by default

## Durable actor bootstrap contract

### Agent namecards

Every long-lived agent should have:
- stable `cardId`
- role
- responsibilities
- reporting relationships
- memory policy
- runtime hints
- bootstrap command

### Workers

Every recurring worker should have:
- stable `worker-id`
- purpose
- wake contract
- runtime hints
- exact execution/bootstrap path
- writable state file for checkpoints

## Context budget policy

Recommended starting limits for disposable helpers:

### Minimal
- packet text target: <= 1800 chars
- total attachments target: <= 12000 chars
- max attachments: 4
- excerpts only

### Targeted
- packet text target: <= 2500 chars
- total attachments target: <= 25000 chars
- max attachments: 8
- excerpts preferred, selective full files allowed

### Extended
- only when justified
- allow full files
- must include a note explaining why minimal/targeted was insufficient

## Robustness rules

1. **One canonical rule home**
   - do not duplicate the same behavioral rule across many root files

2. **Compiled packets for disposable helpers**
   - identity/class rules are resolved before spawn

3. **Local state for durable actors**
   - persistent agents/workers should not depend on vague session history

4. **Report-gap behavior**
   - missing context should be surfaced, not guessed

5. **Parent-controlled widening**
   - only the parent widens context after a failed narrow attempt

6. **Human-readable ids**
   - numeric aliases optional; readable canonical ids preferred

7. **Rollbackable adoption**
   - add the system before deleting old duplicated prompt wording

## Validation

Create a lightweight regression harness for the identity system.

Tests should cover:
- packet size stays within class budget
- forbidden broad reads are absent from compiled packet defaults
- each class emits the expected output contract
- a one-shot child can solve a representative task from the packet alone
- a worker can re-anchor after restart from `spec.json` + `state.json`
- a long-lived agent can re-anchor from its namecard/state without broad memory reads

## Implementation order

### Phase 1 — structure
- add `subagent-classes/`
- write `README.md`
- define 3-5 initial one-shot classes
- keep current `agent-namecards/` and `workers/` as-is

### Phase 2 — packet compiler
- extend/replace `build_subagent_brief.py` so it can accept `--class-id`
- emit packet + attachments + spawn defaults
- enforce size/context budgets in code

### Phase 3 — operating rule update
- update `AGENTS.md` so helpers default to class-compiled packets
- keep durable actors on namecard/worker bootstrap
- explicitly forbid broad workspace reads for disposable helpers unless attached or requested

### Phase 4 — root-file slimming
- once packeted helpers are reliable, trim duplicated subagent guidance from root files
- keep only the canonical startup-core rules always loaded

### Phase 5 — optional advanced runtime hook
- only if still necessary, explore an `agent:bootstrap` hook to swap/add bootstrap context for certain agent classes
- do **not** start here; it is more invasive than the packet-first design

## Recommended first classes

Start with a very small set:
- `oneshot-reviewer`
- `oneshot-verifier`
- `oneshot-researcher`
- `oneshot-editor`
- `oneshot-summarizer`

Do not create a taxonomy explosion early.
If two classes behave the same in practice, merge them.

## Bottom line

The most efficient robust system is:
- **tiny universal bootstrap**
- **durable local identity bundles for durable actors**
- **compiled class packets for disposable helpers**

That gives:
- low token cost for one-shot helpers
- stable identity for long-lived actors
- strong rule coverage
- no dependence on fuzzy inherited memory
- no need to pretend we can message a child before bootstrap exists

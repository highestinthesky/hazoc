---
name: grounded-evolver
description: "Combined safe evolution system for this workspace. Use when you want one practical algorithm that merges proactive continuity, memory-stack discipline, optional typed graph structure, and human-supervised improvement from real signals. Good for deciding what to update, where to write it, what the smallest safe change is, and how to validate it without autonomous loops, cloud memory sprawl, or risky self-modification."
---

# Grounded Evolver

## Overview

Use one combined evolution algorithm for this workspace:

- **Continuity** from `workspace-continuity`
- **Layered memory** from `workspace-memory-stack`
- **Structured relationships** from `workspace-graph`
- **Small safe iteration** from `safe-evolution-loop`

This is the default "improve without drifting" framework.

## The algorithm

### 1. Observe the signal

Start from a real trigger:
- new request
- blocker
- repeated failure
- repeated correction
- cross-channel drift
- decision that changes the plan
- meaningful progress worth preserving

### 2. Generalize the root cause into a reusable moral

Before changing anything, ask:
- **What was the root cause of this problem?**
- **Can that root cause be generalized into a guideline for future work?**
- **Is the guideline broad enough to help on unrelated future tasks, not just this exact incident?**

The goal is to prevent fixing one symptom while leaving the same class of mistake alive.
Prefer morals that change future behavior across many tasks.

Examples of good generalized morals:
- Do not trust surface polish before testing real behavior.
- Fix the interaction model before tuning cosmetics.
- If a control looks immediate, it should behave immediately.
- Protect important state from easy accidental mutation.

### 3. Score what kind of evolution is needed

Ask four questions:
- **How easy is this to lose?**
- **How much does it matter?**
- **Is it repeating?**
- **Does structure matter more than prose?**

### 4. Pick the smallest useful mutation

Possible mutation targets:
- `memory/active-state.md`
- mission-control task board
- `memory/YYYY-MM-DD.md`
- `USER.md`
- `AGENTS.md`
- `.learnings/`
- workspace graph
- a helper script or skill patch

Prefer memory/task/rule updates before code changes.

### 5. Validate before accepting

Every evolution must answer:
- What concrete problem is being solved?
- What is the smallest safe change?
- What proves it helped?
- Where is the result recorded?
- Does the chosen change actually honor the generalized moral from step 2?

For UI work, validation must include both display and behavior:
- check for visual bugs in the real layout/state where the change lives
- test the interaction directly instead of assuming it works from appearance
- verify the control behaves the way it implies (immediate vs saved, safe vs destructive)

### 6. Record and re-anchor

After the change:
- update the right memory layer
- update the task board if it is project work
- add daily-note context if this matters later
- add graph links only when relationships matter

## Default mutation order

Prefer this order unless there is a clear reason not to:

1. update active state
2. update task board
3. append daily note
4. promote durable rule/preference
5. add graph structure if relationships matter
6. patch a helper/skill/workflow if memory alone is not enough

## When to use graph structure

Only use the graph when explicit relationships matter:
- which project owns this task
- which channel raised this request
- which decision affects which task
- which document supports which project

If plain task memory is enough, stay with task memory.

## When to mutate code or skills

Only when the same failure or friction keeps recurring and cannot be solved by better memory/task discipline alone.

Good reasons:
- same manual pattern keeps being repeated
- same misunderstanding keeps recurring
- same context format keeps needing reconstruction

Bad reasons:
- vague desire to become "better"
- curiosity without a real signal
- anything that would require silent autonomous loops

## Guardrails

- do not create autonomous mutation daemons
- do not copy external hub/task/publishing machinery by default
- do not use cloud memory systems as the baseline
- do not perform high-blast-radius changes without oversight
- do not store secrets in memory or graph layers

## Commands

Use the planner script when you want a concrete recommendation:

```bash
python3 skills/grounded-evolver/scripts/grounded_evolve.py \
  --signal "Important Discord request was not copied into main memory" \
  --category cross-channel \
  --repeat-count 2 \
  --impact 4 \
  --loss-risk 5 \
  --cross-channel \
  --project \
  --rule
```

For UI friction, include `--ui` so the plan explicitly checks both display and interaction behavior:

```bash
python3 skills/grounded-evolver/scripts/grounded_evolve.py \
  --signal "Task control looked interactive but did not apply until a separate save" \
  --category correction \
  --repeat-count 2 \
  --impact 4 \
  --loss-risk 3 \
  --project \
  --rule \
  --ui
```

If you already know the abstraction, pass it in explicitly:

```bash
python3 skills/grounded-evolver/scripts/grounded_evolve.py \
  --signal "Task control looked interactive but did not apply until a separate save" \
  --root-cause "The UI implied immediate behavior, but the implementation still depended on a separate save flow." \
  --moral "Do not let controls visually promise behavior they do not immediately perform." \
  --category correction \
  --repeat-count 2 \
  --impact 4 \
  --loss-risk 3 \
  --project \
  --rule \
  --ui
```

## References

- Read `references/algorithm.md` for the full step-by-step model.
- Read `references/mutation-matrix.md` for destination and mutation selection.
- Use `scripts/grounded_evolve.py` to generate a compact evolution plan.

---
name: safe-evolution-loop
description: "Human-supervised improvement loop for the existing workspace. Use when you want to evolve behavior safely from real failures, friction, requests, or repeated work: observe signals, pick the smallest useful improvement, validate it, and record the learning. Good replacement for suspicious self-evolving skills when you want the safe baseframe without autonomous loops, external hubs, auto-publishing, or self-repair machinery."
---

# Safe Evolution Loop

## Overview

Use a small, auditable improvement loop instead of autonomous self-modification.

Keep the frame:
- observe
- extract signals
- choose the smallest worthwhile change
- validate
- record the result

Reject the dangerous parts:
- autonomous daemon loops
- external task marketplaces
- auto-publishing
- auto-reset/repair of git state
- uncontrolled self-modifying code

## The loop

1. Observe a real signal.
2. Translate it into a concrete improvement target.
3. Prefer the smallest safe change.
4. Validate before declaring success.
5. Record the outcome in task memory, daily notes, or `.learnings/`.

See `references/evolution-loop.md` for the detailed checklist.

## Valid signals

Use this skill when the trigger is something concrete:

- repeated mistake
- repeated user correction
- repeated friction in a workflow
- task context is getting lost
- same code/process is being rewritten repeatedly
- a manual step should become a repeatable pattern
- a cross-channel behavior keeps drifting

Do not use vague self-improvement language as a signal by itself.

## Safe mutation rules

Prefer improvements that are:
- local
- reversible
- testable
- aligned with existing workspace rules
- low blast radius

Good targets:
- a skill file
- a helper script
- a task memory template
- an AGENTS.md rule
- a mission-control workflow
- a daily-note/session-end habit

Bad targets by default:
- system prompts
- safety settings
- credentials
- autonomous background loops
- external publishing flows
- git reset / destructive recovery behavior

## Validation rule

Every proposed improvement should answer:
- What problem is it solving?
- What is the smallest change that might solve it?
- How do I know it helped?
- Where should the result be recorded?

If you cannot answer those, the improvement is not ready.

## Recording outcomes

After a successful improvement:
- update the active task if it affects a project
- append a daily-note bullet
- add a durable rule to `AGENTS.md` or `USER.md` if behavior changed
- use `learning-loop` when the issue is a repeat failure or unresolved lesson

## Guardrails

- do not install or run suspicious self-evolution code just because the idea sounds clever
- do not copy network/publishing/self-repair subsystems unless there is a clear approved need
- do not create silent background mutation loops
- do not bypass human oversight for high-blast-radius changes
- do not confuse reflection with permission

## References

- Read `references/evolution-loop.md` for the operational checklist.
- Read `references/rejected-patterns.md` for patterns intentionally excluded from suspicious evolver-style systems.
- Use `scripts/safe_evolution_report.py` to draft a compact improvement report when needed.

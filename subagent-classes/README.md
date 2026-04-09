# Subagent classes

This directory defines **disposable one-shot helper classes**.

Use it for tiny helper roles like:
- reviewer
- verifier
- editor
- researcher
- summarizer

Do **not** use this directory for:
- long-lived agents (`agent-namecards/`)
- recurring workers (`workers/`)

## Contract

A one-shot helper should **not** search the workspace to discover who it is.

Instead:
1. the parent chooses a `classId`
2. the parent reads the class spec here
3. the parent compiles a narrow task packet
4. the child receives that compiled packet at spawn time

So the class files in this directory are mainly **source-of-truth for the parent/orchestrator**, not browse targets for disposable children.

## Default rule

One-shot helpers should be spawned with:
- `mode: run`
- `cleanup: delete`
- minimal or low thinking unless the class says otherwise
- exact excerpts instead of broad workspace reads whenever possible

If the packet is insufficient, the child should **report the gap** rather than widening context on its own.

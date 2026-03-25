---
name: workspace-graph
description: Lightweight typed graph for workspace state. Use when you want structured links between Projects, Tasks, Decisions, Channels, Sessions, Documents, and People; when you need to answer questions like what relates to what, what depends on what, what was decided where, or which task belongs to which project. Better fit than a giant universal ontology when the goal is practical project memory inside this workspace.
---

# Workspace Graph

## Overview

Use a small typed graph for practical project memory. Prefer it when relationships matter more than prose: tasks under projects, decisions tied to channels, sessions tied to work, documents linked to tasks, or dependency chains.

## Use this skill for

- creating structured entities like Project, Task, Decision, Channel, Session, Document, Person
- linking entities with explicit relations
- answering dependency or relationship questions
- tracking where a task came from or where a decision was made
- keeping append-only structured state in the workspace

Do not use this as a replacement for `USER.md`, `MEMORY.md`, or daily notes.
Use it when graph structure adds value.

## Storage

Default files:

- graph: `memory/workspace-graph/graph.jsonl`
- schema: `memory/workspace-graph/schema.json`

Keep writes append-only. Do not rewrite old operations unless the user explicitly wants cleanup.

## Core entity types

Use the built-in practical types first:

- `Project` → named body of work
- `Task` → actionable unit with status
- `Decision` → something decided, with summary and status
- `Channel` → Discord/Telegram/other conversation surface
- `Session` → bounded work session or thread
- `Document` → file or URL worth linking
- `Person` → human or agent participant

See `references/schema.md` for fields and built-in relations.

## Workflow

1. Decide whether a graph is actually useful.
2. Create or query the relevant entities.
3. Add explicit relations instead of implying them in prose.
4. Validate when the graph matters for planning or reporting.
5. Keep the task board and daily notes updated too when the graph reflects real work.

## Commands

Use the bundled script:

```bash
python3 skills/workspace-graph/scripts/workspace_graph.py init
python3 skills/workspace-graph/scripts/workspace_graph.py create --type Project --props '{"name":"Mission Control","status":"active"}'
python3 skills/workspace-graph/scripts/workspace_graph.py create --type Task --props '{"title":"Set up Discord digests","status":"open"}'
python3 skills/workspace-graph/scripts/workspace_graph.py relate --from proj_x --rel has_task --to task_y
python3 skills/workspace-graph/scripts/workspace_graph.py related --id proj_x --rel has_task
python3 skills/workspace-graph/scripts/workspace_graph.py query --type Task --where '{"status":"open"}'
python3 skills/workspace-graph/scripts/workspace_graph.py validate
```

## Practical patterns

### Model project structure

- create one `Project`
- create related `Task` and `Decision` entities
- connect them with `has_task`, `has_decision`, `depends_on`

### Model channel context

- create a `Channel` for `discord:#control-center`
- create `Task` or `Decision` entities for important outcomes
- relate them with `raised_in` or `decided_in`

### Model supporting materials

- create `Document` for key files or URLs
- relate with `documents`, `references`, or `about`

## Guardrails

- never store secrets, tokens, or passwords in entity properties
- keep graph entities concise and factual
- use daily notes for narrative summaries; use the graph for explicit structure
- if a task already exists in mission control, mirror the same idea rather than inventing a separate conflicting reality

## References

- Read `references/schema.md` for the built-in types and relation vocabulary.
- Read `references/query-patterns.md` for common queries and relationship patterns.

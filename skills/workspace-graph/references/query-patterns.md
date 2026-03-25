# Query Patterns

## Common commands

### All open tasks

```bash
python3 skills/workspace-graph/scripts/workspace_graph.py query --type Task --where '{"status":"open"}'
```

### Tasks for a project

```bash
python3 skills/workspace-graph/scripts/workspace_graph.py related --id <project_id> --rel has_task
```

### What depends on this thing?

```bash
python3 skills/workspace-graph/scripts/workspace_graph.py related --id <entity_id> --rel depends_on --dir incoming
```

### Which channel raised this task?

```bash
python3 skills/workspace-graph/scripts/workspace_graph.py related --id <task_id> --rel raised_in
```

### Decisions for a project

```bash
python3 skills/workspace-graph/scripts/workspace_graph.py related --id <project_id> --rel has_decision
```

### Timeline of operations

```bash
python3 skills/workspace-graph/scripts/workspace_graph.py timeline --limit 30
```

## Practical patterns

### Discord request -> task -> project

1. create `Channel` for `discord:#control-center`
2. create `Task`
3. relate `Task --raised_in--> Channel`
4. relate `Project --has_task--> Task`

### Decision traceability

1. create `Decision`
2. relate `Project --has_decision--> Decision`
3. relate `Decision --decided_in--> Channel` or `Session`
4. optionally relate `Document --about--> Decision`

### Documented work session

1. create `Session`
2. relate `Session --about--> Project`
3. relate `Session --about--> Task`
4. relate `Session --involves--> Person`

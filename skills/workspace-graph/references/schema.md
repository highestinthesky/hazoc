# Schema

## Built-in entity types

Use these first before inventing custom types.

### Project

Required:
- `name`
- `status` in `planning | active | paused | archived`

Optional:
- `summary`
- `owner`
- `tags`

### Task

Required:
- `title`
- `status` in `open | in_progress | blocked | done | cancelled`

Optional:
- `priority` in `low | medium | high | urgent`
- `summary`
- `due`
- `source`
- `assignee`

### Decision

Required:
- `title`
- `status` in `proposed | active | superseded | rejected`

Optional:
- `summary`
- `owner`
- `impact`

### Channel

Required:
- `name`
- `platform`

Optional:
- `scope`
- `external_id`

Examples:
- `discord:#control-center`
- `telegram:dm`

### Session

Required:
- `title`
- `status` in `active | paused | ended`

Optional:
- `channel`
- `started_at`
- `ended_at`

### Document

Required:
- `title`

Optional:
- `path`
- `url`
- `summary`
- `kind`

### Person

Required:
- `name`

Optional:
- `role`
- `handle`
- `notes`

## Built-in relations

- `has_task` → Project -> Task
- `has_decision` → Project -> Decision
- `depends_on` → Task -> Task | Project -> Project | Task -> Decision
- `raised_in` → Task | Decision -> Channel | Session
- `decided_in` → Decision -> Channel | Session
- `about` → Document | Session -> Project | Task | Decision
- `references` → Document -> Document | Task | Decision
- `involves` → Session | Project -> Person
- `assigned_to` → Task -> Person

## Usage notes

- Prefer relation names that explain meaning cleanly.
- Keep IDs stable once created.
- Use custom types only when the built-ins are clearly not enough.
- If you add a custom type, document it in the graph schema file with `schema-set` or `schema-merge`.

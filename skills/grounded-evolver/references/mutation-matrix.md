# Mutation Matrix

| Situation | Best first move | Possible second move |
| --- | --- | --- |
| New request | task board | daily note |
| Fragile current context | active-state | task detail |
| Important progress | task detail | daily note |
| Durable user preference | `USER.md` | daily note |
| Durable operating rule | `AGENTS.md` | task detail |
| Repeat failure | `.learnings/` | skill/helper patch |
| Cross-channel important item | task board + daily note | graph link |
| Relationship-heavy project state | graph entry/link | task detail |
| Same workflow pain repeats | workflow/skill patch | AGENTS.md rule |

## Escalation order

Use this escalation ladder:

1. write memory
2. improve task detail
3. add durable rule
4. add graph structure
5. patch skill/helper/workflow

Avoid jumping straight to code when a memory/process fix would solve it.

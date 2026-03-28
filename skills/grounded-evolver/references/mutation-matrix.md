# Mutation Matrix

Choose the learning branch first:
- `build-pattern` when no failed or clearly insufficient protection is known yet
- `repair-pattern` when an existing protection failed or undesirable friction repeated strongly enough to prove the current pattern is insufficient

Then use the matrix below to choose the smallest useful mutation.

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
| UI display/interaction friction | daily note + direct validation pass | workflow/skill patch |

## Escalation order

Use this escalation ladder:

1. write memory
2. improve task detail
3. add durable rule
4. add graph structure
5. patch skill/helper/workflow

Avoid jumping straight to code when a memory/process fix would solve it.

# RECALL_MAP.md

Start narrow. Widen only when answer quality requires it.

## First question

- If the request is self-contained, answer directly.
- If it needs prior context, route to the smallest likely source first.

## Routes

- Preference / durable rule / identity -> `USER.md`, `MEMORY.md`, `PROTOCOL_SPINE.md`
- Active now -> `memory/active-state.md`
- Project/task state -> `scripts/recall_index.py` task route, then `mission-control/data/tasks.json` if needed
- Recent timeline -> `scripts/recall_index.py` recent route, then the relevant daily note if needed
- Older history / dates / decisions -> `MEMORY.md`, then `memory_search`, then daily/task history if needed
- Workflow / protocol detail -> `PROTOCOL_SPINE.md`, then `mission-control/data/protocol.json`, then deep refs
- Branch / agent / worker state -> only if the request actually touches that branch
- Learning / error history -> `.learnings/ERROR_INDEX.md`, then `.learnings/errors/`, then day archives only if needed

## Retrieval routine

1. Route the request.
2. Search the most likely small source first.
3. Load only the smallest useful snippets or line ranges.
4. Widen only if confidence is low.
5. Answer from retrieved context.
6. Write back only the durable result.

## Search defaults

- Prefer routing over broad search.
- Prefer curated memory and compact anchors before raw notes or long task prose.
- Prefer exact snippets before whole-file reads.
- Stop when confidence is good enough; escalate instead of bluffing.
- For prior-work / people / dates / preferences / todos recall, use `memory_search` first when required.

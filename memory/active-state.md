# Active State

## Live anchor (updated 2026-04-02 3:35 PM EDT)
- Mission control is the shared local-first workspace between haolun and hazoc.
- Local URL: `http://127.0.0.1:4180/`.
- Treat this file as live state only. Historical detail belongs in daily notes and task memory.
- The token-efficiency pass is complete: startup prompt was compressed, default/main heartbeat is disabled, default session context is now `160000`, compaction is triggered earlier, and main-task closeout now uses a lightweight best-effort announce path with `--wake now`.
- The cheap recall first pass is now implemented: `PROTOCOL_SPINE.md`, `RECALL_MAP.md`, `scripts/recall_index.py`, and `scripts/build_subagent_brief.py` exist, and `AGENTS.md` / protocol registry were updated to make the behavior durable.

## Current focus
- Validate and tune the new recall-first memory path instead of trimming blindly.
- Working task: `task-design-cheap-memory-recall-path`.

## Next checks
1. Test `scripts/recall_index.py` on active/task/history/protocol queries and tune routing/scoring if needed.
2. Test fresh-session re-anchor against the new startup spine.
3. Test `scripts/build_subagent_brief.py` in `minimal` and `targeted` modes on a real helper task.
4. Tighten wording only after real usage friction shows where it is weak.

## Current caution
- Answer quality beats token savings. If confidence is low, widen retrieval.
- Older long-lived sessions may still show the previous larger footprint until they compact or roll over.

# Active State

## Live anchor (updated 2026-04-02 3:35 PM EDT)
- Mission control is the shared local-first workspace between haolun and hazoc.
- Local URL: `http://127.0.0.1:4180/`.
- Treat this file as live state only. Historical detail belongs in daily notes and task memory.
- The token-efficiency pass is complete: startup prompt was compressed, default/main heartbeat is disabled, default session context is now `160000`, compaction is triggered earlier, and main-task closeout now uses a lightweight best-effort announce path with `--wake now`.
- The cheap recall first pass is now implemented: `PROTOCOL_SPINE.md`, `RECALL_MAP.md`, `scripts/recall_index.py`, and `scripts/build_subagent_brief.py` exist, and `AGENTS.md` / protocol registry were updated to make the behavior durable.
- The recall helper now reads its searchable source registry from `mission-control/data/recall-sources.json` and the always-loaded spine now includes explicit automatic-recall triggers for history/status/protocol/context questions.
- There is now a lightweight regression harness (`scripts/recall_regression.py` + `mission-control/data/recall-regression.json`) to catch common recall-route failures like bad re-anchor or preference/history lookup behavior.
- The latest optimization pass added a real retrieval boundary: compact task/daily anchors are now auto-built under `tmp/recall-anchors/`, `scripts/recall_index.py` indexes them automatically, and task/history recall now prefers those anchors before raw task prose or raw daily logs.

## Current focus
- Validate and tune the new recall-first memory path instead of trimming blindly.
- Working task: `task-design-cheap-memory-recall-path`.

## Next checks
1. See whether mission-control should consume compact task summaries/anchors directly instead of relying only on raw `tasks.json`.
2. Decide whether to split the mission-control frontend (`src/App.jsx`) now or wait until the next UI change batch.
3. Keep watching whether anchor-first recall actually reduces raw-note/task loads in real work.
4. Tighten wording only after real usage friction shows where it is weak.

## Current caution
- Answer quality beats token savings. If confidence is low, widen retrieval.
- Older long-lived sessions may still show the previous larger footprint until they compact or roll over.
- GitHub sync blocker is resolved: the secret-bearing backup snapshot was removed from local history, `.learnings/snapshots/*.bak` is now ignored, and `origin/main` was pushed successfully again.

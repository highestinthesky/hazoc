# Active State

## Live anchor (updated 2026-04-02 8:35 PM EDT)
- Mission control is the shared local-first workspace between haolun and hazoc.
- Local URL: `http://127.0.0.1:4180/`.
- Treat this file as live state only. Historical detail belongs in daily notes and task memory.
- The token-efficiency pass is complete: startup prompt was compressed, default/main heartbeat is disabled, default session context is now `160000`, compaction is triggered earlier, and main-task closeout now uses a lightweight best-effort announce path with `--wake now`.
- The cheap recall first pass is now implemented: `PROTOCOL_SPINE.md`, `RECALL_MAP.md`, `scripts/recall_index.py`, and `scripts/build_subagent_brief.py` exist, and `AGENTS.md` / protocol registry were updated to make the behavior durable.
- The recall helper now reads its searchable source registry from `mission-control/data/recall-sources.json` and the always-loaded spine now includes explicit automatic-recall triggers for history/status/protocol/context questions.
- There is now a lightweight regression harness (`scripts/recall_regression.py` + `mission-control/data/recall-regression.json`) to catch common recall-route failures like bad re-anchor or preference/history lookup behavior.
- The latest optimization pass added a real retrieval boundary: compact task/daily anchors are now auto-built under `tmp/recall-anchors/`, `scripts/recall_index.py` indexes them automatically, and task/history recall now prefers those anchors before raw task prose or raw daily logs.
- The learning-system storage cleanup is now landed: `.learnings/errors/YYYY-MM.md` is the canonical readable error ledger, `.learnings/days/*/error.md` is archive-pointer/day-local context only, the legacy `.learnings/errors.md` landing page was retired into archive, and the learning-loop scripts/docs/checkers were aligned to the new boundary.
- The closeout-path repair is also landed: the helper now normalizes ping wording, uses race-safe pid-scoped temp files for ledger writes, and the two suspicious 2026-04-02 closeout sends were verified via cron run history as `delivered=true`.
- Current open follow-up: main webchat/control UI became unresponsive and incoming messages disappeared until haolun restarted hazoc; the incident is durably logged and is now the next investigation target.

## Current focus
- Investigate the tonight webchat unresponsive/disappearing-message incident now that the requested storage/closeout repairs are complete.
- Keep the repaired learning/error layout and closeout path stable while testing the webchat issue.
- Working task: `task-investigate-webchat-disappearing-messages`.

## Next checks
1. Inspect the restart window for the webchat/session-store behavior that made messages disappear from the control UI.
2. Determine whether the failure lived in the web UI, transcript/session store, or the agent runtime itself.
3. Preserve the new learning/error layout boundary if any follow-up logging is needed.
4. If another closeout ping question comes up, use cron run history plus the local ledger before assuming delivery failed.

## Current caution
- Answer quality beats token savings. If confidence is low, widen retrieval.
- Older long-lived sessions may still show the previous larger footprint until they compact or roll over.
- GitHub sync blocker is resolved: the secret-bearing backup snapshot was removed from local history, `.learnings/snapshots/*.bak` is now ignored, and `origin/main` was pushed successfully again.
- Do not let stale generated recall artifacts or archived task notes override the newly corrected canonical files.

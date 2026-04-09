# Active State

## Live anchor (updated 2026-04-09 4:41 PM EDT)
- Mission control is the shared local-first workspace between haolun and hazoc.
- Local URL: `http://127.0.0.1:4180/`.
- Treat this file as live state only. Historical detail belongs in daily notes and task memory.
- The durable known-good baseline is still the 2026-04-02 optimization batch: startup prompt compressed, default/main heartbeat disabled, default session context `160000`, earlier compaction, lightweight best-effort closeout pings, cheap recall helpers (`PROTOCOL_SPINE.md`, `RECALL_MAP.md`, `scripts/recall_index.py`, `scripts/build_subagent_brief.py`), recall-source registry + regression harness, compact recall anchors under `tmp/recall-anchors/`, cleaned learning/error storage, and `contextPruning` enabled to mitigate tool-output pileup in main.
- No newer user-facing project/task/event progress is visible in the workspace since the last recorded 2026-04-02 maintenance/git-sync window; today’s missing daily note was recreated during hourly maintenance.
- The untracked `memory/2026-04-09-remote-access.md` file preserves a recovered transcript/summary of the 2026-04-02 remote-access planning conversation. As of 2026-04-09, haolun explicitly said to treat that plan as shelved after vacation and not likely to resume any time soon; keep it as historical reference only unless reopened.

## Current focus
- Walk haolun through hazoc's startup process in detail and critique how to make main/subagent context use lighter.
- Working task still open: `task-investigate-webchat-disappearing-messages`.
- Do not present the old 2026-04-02 “tomorrow” Tailscale plan as pending work.

## Next checks
1. Explain the startup sequence clearly, including what is always loaded first versus what stays recall-only until needed.
2. Identify the main remaining token/cache waste: duplicated rules across always-loaded root files, an `active-state` file that is still bulkier than ideal, and helpers that should stay packet-only unless persistence is clearly worth it.
3. Keep watching for any repeat of the old webchat overflow/compaction failure mode if main becomes active again.
4. Keep Discord/Telegram branch agents as scoped/fallback paths only unless an explicit direct-to-main route is built.

## Current caution
- Answer quality beats token savings. If confidence is low, widen retrieval.
- Older long-lived sessions may still show the previous larger footprint until they compact or roll over.
- Do not let stale generated recall artifacts, archived task notes, or old “tomorrow” handoff bullets masquerade as current state.

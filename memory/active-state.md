# Active State

## Live anchor (updated 2026-04-09 4:41 PM EDT)
- Mission control is the shared local-first workspace between haolun and hazoc.
- Local URL: `http://127.0.0.1:4180/`.
- Treat this file as live state only. Historical detail belongs in daily notes and task memory.
- The durable known-good baseline is still the 2026-04-02 optimization batch: startup prompt compressed, default/main heartbeat disabled, default session context `160000`, earlier compaction, lightweight best-effort closeout pings, cheap recall helpers (`PROTOCOL_SPINE.md`, `RECALL_MAP.md`, `scripts/recall_index.py`, `scripts/build_subagent_brief.py`), recall-source registry + regression harness, compact recall anchors under `tmp/recall-anchors/`, cleaned learning/error storage, and `contextPruning` enabled to mitigate tool-output pileup in main.
- No newer user-facing project/task/event progress is visible in the workspace since the last recorded 2026-04-02 maintenance/git-sync window; today’s missing daily note was recreated during hourly maintenance.
- The untracked `memory/2026-04-09-remote-access.md` file preserves a recovered transcript/summary of the 2026-04-02 remote-access planning conversation, but that planning has not yet been durably promoted into current task/state files beyond the older 2026-04-02 handoff language.

## Current focus
- Keep memory/task state honest: do not present the old 2026-04-02 “tomorrow” Tailscale plan as current progress unless fresh work actually resumes.
- Working task still open: `task-investigate-webchat-disappearing-messages`.
- If remote-access work restarts, re-anchor from `memory/2026-04-09-remote-access.md` plus the older 2026-04-02 daily note before changing live state.

## Next checks
1. If active work resumes, decide whether the Tailscale travel-access plan is still current or obsolete before acting on it.
2. Keep watching for any repeat of the old webchat overflow/compaction failure mode if main becomes active again.
3. Keep Discord/Telegram branch agents as scoped/fallback paths only unless an explicit direct-to-main route is built.

## Current caution
- Answer quality beats token savings. If confidence is low, widen retrieval.
- Older long-lived sessions may still show the previous larger footprint until they compact or roll over.
- Do not let stale generated recall artifacts, archived task notes, or old “tomorrow” handoff bullets masquerade as current state.

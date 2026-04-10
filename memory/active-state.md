# Active State

## Current

- Root-prompt slimming pass is in progress: cut always-loaded/startup surface while preserving rule coverage.
- Packet-first disposable-helper scaffolding exists; waiting for haolun to choose concrete one-shot roles.
- `task-investigate-webchat-disappearing-messages` remains open.
- Another brief webchat/control-UI communication failure happened tonight; restart restored contact, so treat this as another recurrence signal for the outage task.
- User-observed symptom to preserve: during the failure, the dashboard reportedly warned that the request could not be sent due to missing/insufficient permissions (exact wording unknown).
- Market-moving digest now has a first script-first local v1 running on user cron: bounded feed collector/scorer, local-only digest outputs, source filters, and an installed low-cost weekday cadence (`*/20 6-18 ET`).
- First low-cost per-user digest fanout now exists: each global digest can emit a shared-global-first user watchlist digest for registered users. `haolun` is the first digest user and currently points at Discord channel `1486030559741349888`.

## Next

1. Finish rule-inventory and coverage tests for root/startup files.
2. Keep shrinking the always-loaded prompt surface safely.
3. If wanted later, auto-use class-aware packet generation in parent spawns.
4. Tomorrow: prioritize more aggressive pruning + cleaner task-local offloading so tool-heavy work stops bloating main; treat a forced 30-minute main reset/rollover only as fallback if those are not enough.
5. If the PC was off overnight, verify the market-digest cron resumed after morning boot; remember nothing runs while the machine is powered off, so the next scheduled tick after boot is the first expected run.
6. Sanity-check the new per-user watchlist digest files/fanout for `haolun`, then decide whether to add delivery and/or richer relevance matching.
7. Optional next market-digest upgrade: enable price enrichment for per-user digests (currently blocked by missing `yfinance`) or swap in another low-cost quote source.
8. Sanity-check the market digest after a few live cron cycles and tighten source filters/ranking if noisy items still leak through.
9. Watch for repeat of the webchat overflow/compaction issue.

## Caution

- Preserve rule coverage before slimming further.
- Answer quality beats token savings.
- `sessions_spawn` attachments are currently disabled here; one-shot tests may need inline excerpts.

# Active State

## Current

- Root-prompt slimming pass is in progress: cut always-loaded/startup surface while preserving rule coverage.
- Packet-first disposable-helper scaffolding exists; waiting for haolun to choose concrete one-shot roles.
- `task-investigate-webchat-disappearing-messages` remains open.
- Another brief webchat/control-UI communication failure happened tonight; restart restored contact, so treat this as another recurrence signal for the outage task.
- Market-moving digest now has a first script-first local v1 running on user cron: bounded feed collector/scorer, local-only digest outputs, source filters, and an installed low-cost weekday cadence (`*/20 6-18 ET`).
- Multi-user digest direction is now explicit: send the shared global digest first, then the user-specific watchlist digest. `haolun` is registered as the first digest user and currently points at Discord channel `1486030559741349888`.

## Next

1. Finish rule-inventory and coverage tests for root/startup files.
2. Keep shrinking the always-loaded prompt surface safely.
3. If wanted later, auto-use class-aware packet generation in parent spawns.
4. Build the next market-digest slice: per-user watchlist relevance + per-user digest files/fanout, starting with `haolun`.
5. Sanity-check the market digest after a few live cron cycles and tighten source filters/ranking if noisy items still leak through.
6. Watch for repeat of the webchat overflow/compaction issue.

## Caution

- Preserve rule coverage before slimming further.
- Answer quality beats token savings.
- `sessions_spawn` attachments are currently disabled here; one-shot tests may need inline excerpts.

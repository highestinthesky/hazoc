# Active State

## Current

- Root-prompt slimming pass is in progress: cut always-loaded/startup surface while preserving rule coverage.
- Packet-first disposable-helper scaffolding exists; waiting for haolun to choose concrete one-shot roles.
- `task-investigate-webchat-disappearing-messages` remains open.
- Market digest worker-first design is drafted and parked.

## Next

1. Finish rule-inventory and coverage tests for root/startup files.
2. Keep shrinking the always-loaded prompt surface safely.
3. If wanted later, auto-use class-aware packet generation in parent spawns.
4. Watch for repeat of the webchat overflow/compaction issue.

## Caution

- Preserve rule coverage before slimming further.
- Answer quality beats token savings.
- `sessions_spawn` attachments are currently disabled here; one-shot tests may need inline excerpts.

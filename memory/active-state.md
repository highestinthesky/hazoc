# Active State

## Current

- Aggressive prompt-surface pruning is done for this mission: `MEMORY.md`, `PROTOCOL_SPINE.md`, and `RECALL_MAP.md` were trimmed, and validation still passes under tighter budgets.
- Haolun wants one mission per session: an explicit "wrap up" means finish the current mission, write back the result/handoff, and stop before the next mission.
- Next mission after reset: investigate `task-investigate-webchat-disappearing-messages`, especially the control-UI permissions-warning clue.
- Market digest v1 is live on user cron, and per-user watchlist fanout exists for `haolun`.

## Next

1. After reset, start the webchat/control-UI investigation from the recurrence notes + permission-warning symptom.
2. Then return to digest fanout/relevance tuning if wanted.

## Caution

- Preserve rule coverage before slimming further.
- Answer quality beats token savings.
- `sessions_spawn` attachments are currently disabled here; one-shot tests may need inline excerpts.

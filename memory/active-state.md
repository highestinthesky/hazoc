# Active State

## Current

- Haolun wants one mission per session: an explicit "wrap up" means finish the current mission, write back the result/handoff, and stop before the next mission.
- Market digest v1 is live on user cron, and the per-user watchlist fanout for `haolun` has now been sanity-checked: broad sector-only false positives were tightened, price enrichment works again through a no-extra-package fallback, and a manual Discord digest send to the configured channel succeeded.
- `task-investigate-webchat-disappearing-messages` is still pending, especially the control-UI permissions-warning clue, but it is no longer the next fresh-session mission.

## Next

1. In the next fresh session, continue `task-market-moving-news-digest` from the new baseline: successful manual Discord send, cleaner personalized matching, and working watchlist prices.
2. Decide whether to formalize recurring Discord delivery now or keep chat delivery manual/local-only for one more short quality pass.
3. After that, return to the webchat/control-UI investigation.

## Caution

- Preserve rule coverage before slimming further.
- Answer quality beats token savings.
- `sessions_spawn` attachments are currently disabled here; one-shot tests may need inline excerpts.

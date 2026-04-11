# Active State

## Current

- Haolun wants one mission per session: an explicit "wrap up" means finish the current mission, write back the result/handoff, and stop before the next mission.
- Market digest v1 is live on user cron, and the per-user watchlist fanout for `haolun` has now been sanity-checked: broad sector-only false positives were tightened, price enrichment works again through a no-extra-package fallback, and a manual Discord digest send to the configured channel succeeded.
- New correction from haolun: the current digest still feels like something he could reproduce with two minutes of manual research. The redesign target is concise but information-dense detail, not a hard cap like "3 items max." Preferred structure: (1) general news and market movers, (2) specific news that will impact a specific stock plus the likely read on that stock, and (3) watchlist-specific news on how watched stocks are likely to change. Sections 1 and 2 are shared/global for all users; section 3 is personalized per user. Keep synthesis, delta-vs-last-run, and watch-next checkpoints, but inside that structure rather than as a separate headline bucket.
- Added a second test digest user profile: `ning` / "Ning". No delivery target or watchlist entries yet.
- Mission-control LAN access from the Mac is now confirmed again. Root cause was browser Local Network permission on macOS, not the server path; the temporary `4173` debug alias was removed, so the stable LAN URL is back on port `4180`.
- `task-investigate-webchat-disappearing-messages` is still pending, especially the control-UI permissions-warning clue, but it is no longer the next fresh-session mission.

## Next

1. In the next fresh session, start `task-display-market-digests-on-website`: build a first read-only mission-control surface for the existing digest artifacts so haolun can review them on the website.
2. Keep that website view aligned with the new digest target shape: shared/global general movers, shared/global stock-impact reads, and a personalized watchlist section.
3. Use the website surface as the next digest-quality review loop, then decide whether recurring Discord delivery should be formalized or remain manual/local-only for one more short pass.
4. Fill in Ning's watchlist and optional delivery target later if/when haolun wants the second test route to emit useful personalized output.
5. After the digest website pass, return to the webchat/control-UI investigation.

## Caution

- Preserve rule coverage before slimming further.
- Answer quality beats token savings.
- `sessions_spawn` attachments are currently disabled here; one-shot tests may need inline excerpts.

# Upstream vetting summary

## Reviewed source skills

- `udiedrichsen/stock-analysis`
- `matagul/desktop-control`

## `stock-analysis` assessment

Risk: **medium-high**

Why:
- useful public-data market tooling exists in the codebase
- but the skill scope sprawls into Twitter/X social scraping, rumor detection, and token-driven bird CLI usage
- docs instruct users to create `.env` with `AUTH_TOKEN` / `CT0`
- docs mention installing/running extra binaries and storing state under `~/.clawdbot/...`
- metadata underspecifies the sensitive auth and storage behavior compared with what the docs/scripts actually do

What I kept conceptually:
- compact ticker snapshots
- simple comparisons
- watchlist + target / stop state

What I rejected:
- browser-cookie / token workflows
- Twitter/X integration
- rumor scanner / buzz scraping
- hidden home-directory persistence
- oversized all-in-one analysis claims

## Fork design choice

`market-watch` is intentionally narrower and safer:
- public quote/history data only
- local state under the skill folder
- no social scraping
- no auth-token handling
- no autonomous cron behavior by default

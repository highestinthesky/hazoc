# Watchlist data model

Path:
- `state/watchlist.json`

Each item:

```json
{
  "ticker": "AAPL",
  "target": 220.0,
  "stop": 180.0,
  "note": "AI basket",
  "createdAt": "2026-03-25T02:00:00+00:00"
}
```

Design notes:
- workspace-local, not hidden in `~/.clawdbot`
- one flat list for easy grep/edit/recovery
- no secrets stored here

# Market digest state model

Paths:
- `state/digest/observations.jsonl` — normalized recent observations with scores / eligibility flags
- `state/digest/last_seen.json` — dedupe keys with last-seen timestamps
- `state/digest/source-health.json` — fetch status + HTTP cache hints per source
- `state/digest/digest-worker-state.json` — local runner state
- `state/digest/digests/YYYY-MM-DD/<window>.md` — rendered digest markdown
- `state/digest/digests/YYYY-MM-DD/<window>.json` — rendered digest JSON
- `state/digest/latest.md` / `latest.json` — latest emitted digest copies

Observation shape (compact example):

```json
{
  "id": "c6ac7f4b20f8f4a0",
  "seenAt": "2026-04-09T23:55:00+00:00",
  "eventTime": "2026-04-09T23:40:59+00:00",
  "source": "Yahoo Finance",
  "sourceId": "yahoo-finance-news",
  "headline": "Example headline",
  "url": "https://finance.yahoo.com/...",
  "category": "general-market",
  "themes": ["ai-chips"],
  "score": 9.25,
  "digestEligible": true,
  "highPriority": false,
  "affectedSectors": ["Technology", "Semiconductors"],
  "affectedNames": ["NVDA"],
  "affectedEtfs": ["SMH", "XLK", "QQQ"]
}
```

Digest design notes:
- normalized + scored locally first; no raw HTML blobs kept in state
- only bounded recent history is retained
- state is meant to stay inspectable and recoverable with plain-text tools

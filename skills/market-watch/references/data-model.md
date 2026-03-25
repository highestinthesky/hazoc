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

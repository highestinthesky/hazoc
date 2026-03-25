---
name: market-watch
description: Safe, workspace-local stock and crypto research for quote snapshots, simple comparisons, and watchlist checks using public market data only. Use when someone asks for a ticker overview, a compact multi-ticker compare, or a local watchlist/price alert workflow without social scraping, browser cookies, or hidden state outside the workspace.
---

# Market Watch

## Overview

Market Watch is my safer fork of the upstream stock-analysis idea. It keeps the useful core — quote snapshots, lightweight technical context, and a local watchlist — while deliberately cutting the risky parts like Twitter/X cookie flows, rumor scraping, hidden home-directory state, and overgrown all-in-one analysis claims.

## When to use this skill

Use this skill when the request is about:
- a quick stock or crypto snapshot
- comparing a small set of tickers
- checking simple trend / moving-average / RSI context
- maintaining a local watchlist with target / stop reminders

Do **not** use this skill for:
- scraping private social feeds
- extracting browser cookies or auth tokens
- autonomous trading or financial advice
- hidden cron/state outside the workspace

## Quick start

### 1. Snapshot one or more tickers

```bash
python3 {baseDir}/scripts/market_snapshot.py AAPL
python3 {baseDir}/scripts/market_snapshot.py AAPL MSFT NVDA
python3 {baseDir}/scripts/market_snapshot.py BTC-USD ETH-USD --json
```

### 2. Maintain a local watchlist

```bash
python3 {baseDir}/scripts/watchlist.py add AAPL --target 220 --note "AI basket"
python3 {baseDir}/scripts/watchlist.py list
python3 {baseDir}/scripts/watchlist.py check
python3 {baseDir}/scripts/watchlist.py remove AAPL
```

## Workflow

### A. Snapshot first

Start with `market_snapshot.py` unless the user explicitly asked for watchlist management.

What it gives:
- latest price
- 1d / 5d / 1m return context
- 52-week range position
- SMA20 / SMA50 trend context
- RSI14 when enough history exists
- dividend yield when available

### B. Compare compactly

For multiple tickers, run one command with all symbols instead of looping one-by-one when possible.

Good examples:
- "Compare AAPL, MSFT, NVDA"
- "Give me a fast read on BTC-USD and ETH-USD"

### C. Use watchlist only for durable follow-up

Use the local watchlist when the user wants ongoing reference state like:
- target price
- stop level
- note / thesis fragment

State lives under the skill folder, not in a hidden home-directory tree.

## Safety posture

- Public market data only.
- No browser-cookie extraction.
- No Twitter/X auth flows.
- No rumor scanner.
- No autonomous cron behavior unless explicitly asked later.
- Not investment advice; treat output as research context.

## Resources

### scripts/
- `market_snapshot.py` — quote snapshot and compact analysis
- `watchlist.py` — workspace-local watchlist CRUD + alert checks

### references/
- `vetting.md` — what I kept vs rejected from the upstream skill
- `data-model.md` — watchlist/storage format

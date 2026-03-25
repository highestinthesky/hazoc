# Market-moving news digest plan

## Product goal

Build a bounded public-source digest system that:
- gathers the most important market-moving headlines
- infers likely affected sectors / important stocks / ETFs
- ranks by significance
- compiles interval-based digests for haolun

This is **not** meant to start as a ticker-specific watchlist monitor.

## Source tiers

### Tier 1 — primary / official
Use these first whenever possible.

- Federal Reserve releases / speeches / statements
- BLS releases (CPI, jobs, PPI)
- Treasury / government macro releases
- SEC / EDGAR filings
- company investor-relations pages / press releases / earnings releases

### Tier 2 — major public news
Use as broad coverage + confirmation.

- Reuters public pages
- Yahoo Finance public pages
- CNBC public pages
- MarketWatch public pages
- Google News / public RSS feeds

### Tier 3 — optional later
Only add if haolun explicitly wants more noise / earlier signals.

- broader public discussion sources
- noisier sentiment / forum inputs

## First scoring model

Each item gets scores for:
- **macro importance** — rates, inflation, jobs, energy, war, regulation, AI/chips, major earnings, M&A
- **surprise / novelty** — is this new, unexpected, or materially changed?
- **breadth** — broad-market, sector-wide, or single-name
- **source quality** — official > top-tier news > secondary pickup
- **confirmation** — repeated by multiple credible sources
- **affected-name significance** — does it hit major index names / critical ETFs / market bellwethers?

## Inference targets

For each accepted item, infer:
- likely affected sectors
- likely affected stocks
- likely affected ETFs / indices
- direction if reasonably inferable
- confidence level

## Digest item format

- **headline**
- **why it matters**
- **likely affected sectors / stocks / ETFs**
- **impact scope**: broad / sector / single-name
- **confidence**
- **source(s)**

## Delivery modes to support

### default digest cadences to consider
- morning setup digest
- midday update
- evening wrap-up

### optional later
- urgent alert when a score crosses a high threshold

## Storage model

Suggested files under `skills/market-watch/state/`:
- `observations.jsonl` — raw structured accepted items
- `digests/YYYY-MM-DD.json` — compiled digest payloads
- `last_seen.json` — dedupe / freshness state
- `source-health.json` — fetch success / error tracking

## First implementation slices

1. **source adapters**
   - fetch major public pages / feeds
   - normalize headlines and timestamps
2. **impact scoring**
   - compact rules-based scorer first
3. **affected-name inference**
   - sectors / bellwethers / ETF mapping
4. **digest compiler**
   - rank + dedupe + summarize
5. **delivery**
   - start with local output / mission-control storage
   - later add routed message delivery

## Tomorrow starting point

- confirm exact source allowlist
- define the first digest cadence
- implement Tier 1 + Tier 2 fetchers only
- keep the first version bounded, deterministic, and auditable

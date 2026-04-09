# Hourly digest worker v1

## Status

Drafted on 2026-04-09.
Temporarily parked until haolun is ready to resume this line of work.

## Recommendation summary

For the market-moving digest, use a **worker-first** architecture:

- **recurring low-thinking worker** = fetch, normalize, dedupe, score, store
- **disposable low-thinking child** = summarize accepted items only when there is enough new material
- **optional disposable verifier child** = only for higher-stakes digests or spot checks

Do **not** make a fresh one-shot web-scraper child the primary hourly loop.
That would be less efficient because it pays startup cost every run, carries weaker dedupe memory, and makes source coverage less deterministic.

## Product goal

Build a bounded public-source digest system that:
- gathers important market-moving headlines
- infers likely affected sectors / bellwethers / ETFs
- compiles interval-based summaries
- stays auditable, local-first, and cheap to run

This is **not** a ticker-by-ticker passive watcher in v1.

## First-shippable operating shape

### Cadence

Recommended initial cadence:
- weekdays only
- hourly during market-relevant hours
- suggested first window: 8 AM–6 PM America/New_York

Example cron later:
- `5 8-18 * * 1-5` in `America/New_York`

Reason:
- cheaper than true 24/7 hourly
- still catches premarket / market / after-close headlines
- easier to audit early behavior

## Core actors

### 1) Recurring worker

Proposed worker id:
- `market-moving-digest-hourly`

Purpose:
- perform the cheap deterministic part of the loop
- own freshness, dedupe, and source-health state
- decide whether a summarizer child is worth spawning

Runtime posture:
- thinking: low
- reasoning: off unless debugging requires otherwise
- deterministic bounded source allowlist only

### 2) Disposable summarizer child

Use when:
- new accepted observations in the current window exceed a minimum threshold
- or one item crosses a high significance threshold

Current likely class:
- generic `oneshot-summarizer` for early testing

Later likely dedicated class:
- `oneshot-market-digest-summarizer`

Purpose:
- receive only accepted observations/snippets for the current window
- produce a compact digest with no extra browsing

### 3) Optional verifier child

Use when:
- the digest includes especially consequential claims
- or the worker confidence is low but the item seems important

Current likely class:
- generic `oneshot-verifier`

Later likely dedicated class:
- `oneshot-market-digest-verifier`

Purpose:
- check whether the draft digest actually matches the provided observations and citations

## Source allowlist

### Tier 1 — official / primary

Use first whenever possible:
- Federal Reserve releases / statements / speeches
- BLS releases
- Treasury releases
- SEC / EDGAR filings
- company IR / earnings / press-release pages

### Tier 2 — major public news

Use as broad coverage plus confirmation:
- Reuters public pages
- Yahoo Finance public pages
- CNBC public pages
- MarketWatch public pages
- public RSS / Google News where appropriate

### Tier 3 — later only

Do not use in v1 unless explicitly requested:
- noisier public chatter sources
- sentiment-heavy or rumor-heavy feeds

## Local state

Suggested paths under `skills/market-watch/state/`:

- `observations.jsonl` — accepted normalized observations
- `digests/YYYY-MM-DD.json` — compiled digests
- `last_seen.json` — dedupe / freshness markers by source
- `source-health.json` — fetch status and failures
- `digest-worker-state.json` — worker-local status / last run / last digest window / counters

If a formal managed worker is created later, its durable identity should also live under:
- `workers/market-moving-digest-hourly/spec.json`
- `workers/market-moving-digest-hourly/state.json`

## Observation schema

Each accepted observation should include at minimum:
- `id`
- `seenAt`
- `eventTime` if known
- `source`
- `sourceTier`
- `headline`
- `url`
- `summary`
- `category`
- `macroImportance`
- `novelty`
- `breadth`
- `sourceQuality`
- `confirmationCount`
- `affectedSectors`
- `affectedNames`
- `affectedEtfs`
- `direction` if reasonably inferable
- `confidence`
- `digestEligible`
- `dedupeKey`

## Worker loop

### Step 0 — bootstrap
- load worker identity/state
- confirm current window and last successful run

### Step 1 — fetch
- fetch only the bounded allowlist
- record source health and fetch errors
- do not do broad roaming web search as the default loop

### Step 2 — normalize
- extract headline, timestamp, source, URL, and short raw summary
- normalize source names and timestamps
- generate `dedupeKey`

### Step 3 — dedupe + freshness filter
- compare against `last_seen.json` and recent `observations.jsonl`
- suppress unchanged repeats
- merge repeated coverage where appropriate

### Step 4 — score
- score each candidate for:
  - macro importance
  - novelty
  - breadth
  - source quality
  - confirmation
  - affected-name significance

### Step 5 — infer affected areas
- infer likely sectors
- map likely bellwethers / important names
- map likely ETFs / indices
- keep a confidence field

### Step 6 — accept or discard
- only persist items that meet minimum digest-worthiness
- write accepted items to `observations.jsonl`

### Step 7 — decide whether to summarize
- if no meaningful new items: stamp state and exit quietly
- if enough new items exist: build a narrow packet for a summarizer child
- if only one or two minor items exist: optionally defer until the next window

### Step 8 — summarize
- spawn a disposable low-thinking summarizer child
- provide only accepted observations/snippets from the current window
- child returns a structured digest draft

### Step 9 — optional verify
- only for high-stakes or uncertain windows
- spawn a disposable verifier child against the worker packet + summary draft

### Step 10 — store digest
- write final digest payload locally
- update worker state with digest window and counts

### Step 11 — delivery boundary
V1 recommendation:
- local storage only
- optionally mission-control storage/view later
- no automatic cross-channel push until digest quality is stable

## Spawn packet shape for summarizer child

The child packet should include only:
- digest window
- goal
- expected output
- acceptance checks
- accepted observations/snippets for that window
- explicit guardrail: do not browse for extra context

The child should **not** read:
- task board
- `memory/active-state.md`
- daily notes
- broad workspace files
- arbitrary web sources

## Suggested digest output shape

Each digest item:
- headline
- why it matters
- likely affected sectors / names / ETFs
- scope: broad / sector / single-name
- confidence
- supporting sources

Digest-level metadata:
- window start / end
- total sources checked
- accepted observation count
- top categories
- unresolved uncertainties

## Efficiency rules

1. worker owns state, not the child
2. source allowlist stays bounded
3. one-shot child is packet-only
4. no broad search unless explicitly escalated
5. skip child spawn if there is nothing worth summarizing
6. prefer deterministic scoring before model synthesis
7. keep v1 local-only until quality is proven

## Why this is more efficient than an hourly one-shot scraper

Because the recurring worker can remember:
- what it has already seen
- which sources are healthy
- what changed since last run
- whether there is enough novelty to justify synthesis

A fresh one-shot scraper every hour would have to rediscover all of that each time.

## Good first implementation slices

1. define exact source allowlist
2. implement fetch + normalize
3. implement dedupe + observation storage
4. implement rules-based scoring
5. implement worker decision to summarize-or-skip
6. add summarizer child packet flow
7. only later add delivery

## Explicitly deferred for now

- urgent push alerts
- broad noisy sentiment sources
- autonomous ticker coverage expansion
- social scraping
- heavy reasoning per run
- 24/7 cadence by default

## Hold note

This draft exists so the design is ready to resume without re-deriving it.
Until haolun explicitly reopens it, treat this as **parked design work**, not active implementation.

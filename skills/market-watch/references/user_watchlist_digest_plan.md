# User-aware watchlist digest plan

Goal: keep one cheap shared market worker, then fan out a shared-global-first plus user-specific digest for each registered user.

## Desired delivery order

For each user delivery route:
1. shared global digest
2. user-specific watchlist digest

This preserves common market context while still making each user feel personally served.

## Core architecture

- One shared collector fetches/normalizes/dedupes/scans public feeds.
- One shared observation store remains the source of truth.
- One batched quote pass fetches the union of all watched tickers.
- Per-user matching/ranking happens from local state after collection.
- Per-user rendering happens after the global digest is available.

## User model

Config path:
- `config/digest_users.json`

Each user should have:
- `userId`
- `displayName`
- `timezone`
- `enabled`
- `watchlistEnabled`
- one or more delivery routes

## Watchlist model

State path:
- `state/watchlist.json`

Each watch item should have:
- `userId`
- `ticker`
- optional `target`
- optional `stop`
- optional `note`
- optional `aliases`
- optional `importance`

## Digest flow

1. Collect global observations.
2. Compile/write the shared digest.
3. Load registered users + watchlists.
4. Build the union of watched tickers and fetch prices once.
5. Score each observation for per-user relevance:
   - direct ticker/company mention
   - likely affected-name match
   - sector/theme relevance
   - price movement / target / stop events
   - user importance boost
6. Write per-user digest files.
7. Deliver global first, then user-specific.

## V1 inclusion rules for a user's watchlist section

Include an item if any of these are true:
- direct ticker/company match
- target/stop hit
- strong single-day move
- matched observation score crosses a per-user threshold
- item is globally high-priority and overlaps the user watchlist by sector/name/theme

## Suggested output split

### Global digest
- same for everyone
- broad market / macro / major sector movers

### User digest
- only that user's watched names
- latest price / move
- target/stop flags
- matched headlines
- short why-it-matters note

## Efficiency guardrails

- never re-fetch feeds per user
- never re-fetch prices per user
- keep recurring work script-first
- only use a model for optional polish later, not for the constant loop

# .learnings

This directory is the canonical holding area for **lessons that are not yet fully promoted**.

It is not the final home for accepted operating protocols.
Accepted protocols should be promoted into their canonical operating file and then indexed in `mission-control/data/protocol.json`.

## Storage model

### Draft lessons

- `LEARNINGS.md` -> draft lessons, corrections, better practices, recurring patterns that are still being tested or are not yet promoted
- `FEATURE_REQUESTS.md` -> missing capabilities, future tools/views, explicit later ideas

### Error evidence

- `errors.md` -> short landing page / format guide
- `errors/YYYY-MM.md` -> actual error entries, grouped by day

## Accepted protocols

Accepted protocols do **not** stay only in `.learnings/`.
When a lesson becomes an accepted operating protocol:

1. write the real operating text into its canonical home
   - `AGENTS.md` for global operating rules
   - `TOOLS.md` for environment/tool-specific rules
   - skill docs for workflow-specific rules
2. add or update its registry entry in `mission-control/data/protocol.json`
3. leave `.learnings/` as the draft/evidence trail, not the only source of truth

## Why this split

- lessons and protocols have different lifecycles
- `.learnings/` should stay a compact staging/evidence area
- accepted protocols need a visible registry plus a canonical operating file
- this avoids creating one giant mixed file with drafts, failures, and active rules all tangled together

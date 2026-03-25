# Rejected Patterns

These are common suspicious or overreaching patterns in self-evolving systems that are intentionally excluded here.

## Rejected by default

- autonomous background mutation daemons
- external task marketplaces feeding unsupervised work
- automatic publishing of generated skills or assets
- git hard resets / self-repair that can destroy local state
- uncontrolled network sync of internal memory
- environment fingerprinting beyond a clear local need
- changing safety-critical behavior without explicit oversight
- broad self-modification frameworks that touch everything at once

## Why reject them

They increase blast radius faster than they increase reliability.
The safe part of evolution is not autonomy; it is disciplined iteration.

## What to do instead

Use:
- explicit triggers
- small scoped changes
- local validation
- visible memory updates
- human review for high-impact changes

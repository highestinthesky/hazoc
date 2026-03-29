# errors

Landing page for repeatable failures, broken workflows, and debugging notes.

## Structure

- keep the index file short: `.learnings/errors.md`
- for completed learning runs, store full problem detail in `.learnings/days/YYYY-MM-DD/error.md`
- older compact month logs remain in `.learnings/errors/YYYY-MM.md`
- use the daily `error.md` path when you want the full incident record, not just a terse bug note

## Entry format

Daily `error.md` files should keep one section per learning run and include:
- run id / time
- succinct summary
- full problem details
- context / root cause
- lessons captured
- protocol outcomes
- changes / validation

## Why this shape

- the detailed record for a learning run lives with that day
- the terse daily note stays compact
- lessons and protocol outcomes can be distilled separately into `.learnings/LEARNINGS.md` and `.learnings/PROTOCOLS.md`

Legacy month logs still live in `.learnings/errors/`.

# .learnings layout

This folder has four different jobs. Keep them separate.

- `LEARNINGS.md` — promoted durable lessons
- `PROTOCOLS.md` — promoted workflow/protocol changes
- `errors/` — canonical readable error history, organized by month
- `days/YYYY-MM-DD/` — day-scoped raw/archive capture only

## Reading order

If you want to understand what went wrong, read in this order:
1. `errors/YYYY-MM.md`
2. `ERROR_INDEX.md`
3. `days/YYYY-MM-DD/` only when you need date-local raw context

## Important boundary

- Do **not** treat `days/` as the main readable error ledger.
- Day folders are archive/capture surfaces.
- Canonical error history lives in `errors/`.

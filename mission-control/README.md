# Hazoc Mission Control

Local-first mission-control workspace for haolun and hazoc.

## Runtime modes

- `npm run dev` → Vite dev UI on `127.0.0.1:4173`
- `npm run dev:lan` → Vite dev UI on `0.0.0.0:4173`
- `npm run build` → build the frontend bundle
- `npm run start` → stable single-server runtime on `0.0.0.0:4180`

## Current app structure

- **Tasks** → shared request memory and project detail editing
- **Schedule** → planned task calendar in `America/New_York`
- **Recurring duties** → separate operational rhythm panel on the schedule page
- **Memory** → active state, curated context, and recent daily notes

## Notes

- The stable runtime serves both the frontend and `/api/*` from one Express process.
- Static responses are sent with no-store headers to reduce stale bundle/cache weirdness.
- LAN access depends on host networking and firewall rules in addition to the app binding.

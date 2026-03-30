# Mission-control data files

This folder mixes a few kinds of data. The important distinction is **live state vs durable configuration**.

## Live shared state

- `tasks.json` -> shared task board state
- `events.json` -> user event store
- `main-task-closeouts.json` -> queued/sent Discord completion closeouts

These files change during normal operation.

## Durable operating configuration

- `notifications.json` -> notification routing and closeout behavior
- `protocol.json` -> standing operating rules mirrored into the app
- `recurring.json` -> recurring duty descriptions shown in the UI

These change when the operating model changes, not on every normal run.

## Notes

- Treat `main-task-closeouts.json` as a queue/state file, not a documentation file.
- Keep queue/state, config, and UI descriptions conceptually separate even if they live in the same folder today.
- If this folder grows more crowded later, the next structural cleanup would be splitting `state/` from `config/`.

# TOOLS.md - Local Notes

## Messaging / reminders

- Visible timed pings need explicit chat delivery / announce behavior; a main-session `systemEvent` alone is not enough for in-channel reminders.
- Main task closeout helper: `scripts/main_task_closeout.py`
- Main task closeout config: `mission-control/data/notifications.json`
- Closeout ledger: `mission-control/data/main-task-closeouts.json`

## Git / GitHub

- Keep `.learnings/snapshots/*.bak` out of git.
- If `scripts/git-auto-sync.sh` reports `push_failed`, inspect `detail=` before assuming SSH/auth is broken.

## Mission control / LAN

- If a Mac browser says a local mission-control URL is unreachable while `curl` to the same `http://<LAN-IP>:<port>/` works, check macOS **System Settings → Privacy & Security → Local Network** for that browser before changing the server or Windows/WSL bridge.

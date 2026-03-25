# Active State

## Fresh-chat anchor
- Mission control is the shared local-first workspace between haolun and hazoc.
- Use `http://127.0.0.1:4180/` for mission control right now; 4173 had stale/dev-server issues.

## What exists now
- Tasks page with detailed task memory and lane management.
- Schedule page using task dates/times in `America/New_York`.
- Memory page reading real workspace memory files.
- Recurring duties visible on Schedule.

## Core operating rules
- Per meaningful message: triage task -> create/update task -> adjust lane.
- Review/update task board roughly hourly while active.
- Mirror important Discord/Telegram items back into main project memory.
- Push meaningful GitHub changes once per hour while active, aligned to `:30`; a recurring reminder only counts after a real commit/push or a verified clean/no-change check.
- Keep mission control up while active.
- Use memory retrieval before answering new meaningful questions.

## Default systems
- Continuity stack: active-state + task board + daily note + curated memory.
- Evolution framework: `grounded-evolver` first; supporting modules only as needed.
- Video analysis: `youtube-watcher` + `video-frames` together by default.

## Messaging state
- Discord: configured; control-center is the main server channel; haolun is the intended command source.
- Telegram: DM-only; allowlisted sender `8635838230`.

## Important next-step reminder
- Start the next conversation fresh and re-anchor from this file + today's memory note instead of dragging the old thread forward.

## Latest upgrade
- Mission control now runs stably on port 4180 with `HOST=0.0.0.0`.
- LAN bridge was added on Windows so the current Wi-Fi/LAN URL should be `http://192.168.12.190:4180/`.
- Schedule page now has clearer separation: calendar, upcoming tasks, recurring duties, and unscheduled work each have their own area.
- New feedback from haolun: the site now works on Mac over LAN, but the current UI still feels visually ugly/clunky and needs another polish pass.

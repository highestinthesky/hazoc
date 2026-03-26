# Active State

## Fresh-chat anchor
- Mission control is the shared local-first workspace between haolun and hazoc.
- Use `http://127.0.0.1:4180/` locally for mission control right now; 4173 had stale/dev-server issues.
- Current LAN URL is `http://192.168.12.188:4180/`.

## What exists now
- Tasks page with detailed task memory and section management across Workbench, On Hold, and Archived; the old Capture Tray has been removed.
- Protocol page now holds standing operating rules plus recurring rhythm, so Workbench stays focused on real project work instead of duties.
- Schedule page is now event-first in `America/New_York`, with scheduled user events separated from hazoc work tasks.
- Events page stores scheduled events separately so they can be reviewed and archived cleanly.
- Memory page reads real workspace memory files.

## Core operating rules
- Per meaningful message: triage task -> create/update task -> adjust lane.
- Run a full hourly memory optimization + task board update while active, not just a superficial board skim.
- Mirror important Discord/Telegram items back into main project memory.
- Push meaningful GitHub changes once per hour while active, aligned to `:30`; a recurring reminder only counts after a real commit/push or a verified clean/no-change check.
- Keep mission control up while active.
- Before any meaningful action, do a quick harm check: could this be harmful in any way? If yes or unclear, reduce blast radius or ask.
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

## Current session anchor (2026-03-26 18:16 EDT)
- Re-anchored after reset from active-state, today's note, curated memory, and the mission-control task board.
- Current workbench priorities remain:
  - mission-control UI polish, starting with visual hierarchy and scanability
  - market-moving news digest design, starting with a bounded source allowlist and observation schema
  - multi-user schedule architecture, starting with profile registry + event ownership rules
- No new blocker surfaced during re-anchor; the main known open issue is still that mission control works but the UI feels visually clunky and needs another polish pass.
- If work resumes immediately, default first move is to either do the visual hierarchy polish slice or formalize the digest source/schema spec.
- Fresh UI preference from haolun: strip self-explanatory page/context boxes and keep mission control utility-first rather than explaining pages back to ourselves.

## Handoff for tomorrow
- First confirm the Protocol page / Workbench split feels right in the live UI.
- If continuing mission-control UI work, start with the safest/highest-signal polish slices: visual hierarchy first, then task/event scanability.
- If switching to the digest build, start under `skills/market-watch` with the bounded source allowlist, `sources.json`, observation schema, and polling loop before scoring or delivery.
- For multi-user scheduling, the next key design choice is whether “add to another user” means shared attendees or separate personal copies, then define reminder-channel rules.
- Mission control should already auto-recover and be reachable at `http://192.168.12.188:4180/` after login/reboot via the watchdog + bootstrap path.

## Latest upgrade
- Mission control now runs stably on port 4180 with `HOST=0.0.0.0`.
- LAN bridge is working and the current Wi-Fi/LAN URL is `http://192.168.12.188:4180/`.
- Mission-control uptime is now boot-persistent in two layers: a real `systemd --user` service (`mission-control-watchdog.service`) inside WSL plus a Windows logon task (`HazocMissionControlBootstrap`) that wakes WSL and starts the watchdog after reboot/login.
- Protocol page was added so standing rules and recurring duties have their own home, and the obvious duty-items were moved out of Workbench into Protocol/archived history.
- New feedback from haolun: the site now works over LAN, but the current UI still feels visually ugly/clunky and needs another polish pass.
- Schedule page now has a direct-to-hazoc request textbox with inline replies / clarifying questions.
- Scheduled events are now separated from tasks: dedicated `mission-control/data/events.json`, event API/routes, event-first schedule calendar, and a separate Events page with archiving.
- Longer-term schedule plan still pending: support 4 schedule profiles (hazoc, haolun, and two more users), allow one request to place an event onto another user's schedule too, and eventually connect profiles to Google Calendar plus Discord/Telegram reminders.
- While haolun is away, default to low-risk internal work: keep uptime healthy, tighten active/task memory, turn rough mission-control polish goals into smaller slices, and refine the market-digest / multi-user schedule plans into cleaner next steps.
- Planning refinement completed in task memory: mission-control polish is now split into visual hierarchy, scanability, schedule/events distinction, and a small QA sweep; the market-digest and multi-user schedule tasks now include cleaner ordered execution slices.

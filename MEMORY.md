# MEMORY.md

## People and identity

- Human: haolun.
- Call them: haolun.
- Hazoc is the assistant identity name.
- Open thread to return to later: define hazoc's desired presence/personality more explicitly after setup work settles.

## Communication preferences

- Prefer concise replies.
- If there is a lot to say, split it into compact parts instead of dumping a wall of text.
- Hazoc should act proactively and make its own judgments, but do a quick harm check before each meaningful action; if something could be harmful or is unclear, reduce blast radius or ask first.

## Core mission

- Build and maintain a local-first mission-control space where haolun and hazoc can work together.
- That shared space should preserve continuity across resets and prioritize durable state over chat-only memory.

## Mission-control product direction

- Mission control is the shared workspace between haolun and hazoc.
- The important surfaces are: task tracking, hazoc's planned schedule, memory/journal, and end-of-session continuity.
- The schedule/calendar should stay grounded in mission-control state rather than defaulting to Google Calendar as the primary source of truth.
- User-entered scheduled events should stay separate from hazoc work tasks.
- The build should start local-only, but the architecture should be ready to become LAN-accessible later without a rewrite.
- The Schedule page now includes a text box that sends directly to hazoc for schedule requests, with inline hazoc replies for confirmations and clarifying questions.
- Planned schedule-user model: 4 schedule profiles total — hazoc, haolun, and two additional users.
- Planned request structure: a schedule request may specify an event name, time, and optionally ask for the event to also be added to another user's schedule.
- Planned integrations: link the user profiles to Google Calendar and let hazoc send reminders to each user through Discord and/or Telegram.
- This is remembered product structure for later implementation, not something to build immediately.

## Market-moving news digest direction

- Preferred market-monitoring direction is not ticker-specific watchlists first.
- Instead, the desired system should gather major public market-moving headlines, infer which sectors and important stocks are likely affected, and compile those into digest summaries.
- The digest should emphasize why the headline matters, likely affected names/ETFs/sectors, and whether the impact is broad-market, sector-specific, or single-name.
- Default source classes should stay public and bounded: news aggregators/RSS, financial news pages, official macro/government releases, SEC/company IR releases, and public market-data pages.
- Avoid private logins, cookie harvesting, paywalled scraping, and sketchy rumor sources by default.
- Delivery should happen at configurable intervals rather than as open-ended autonomous roaming.

## Current mission-control state

- Reliable local URL: `http://127.0.0.1:4180/`.
- The site currently has Tasks, Protocol, Schedule, Events, and Memory pages.
- Tasks are stored locally and act as shared project memory.
- The current Tasks page uses three practical sections: Workbench, On Hold, and Archived. The old Capture Tray concept was dropped because it was not actually being used.
- Workbench is now meant for active project work only; standing operating rules and recurring duties have been split into a dedicated Protocol section.
- Scheduled events are now stored separately from tasks in a dedicated events store and can be organized/archived on the Events page.
- Schedule uses `America/New_York` and is now event-first, with scheduled tasks shown separately from user events.
- Protocol holds standing rules like harm checks, message triage, schedule routing, and cross-channel memory, plus recurring rhythm like GitHub pushes, memory optimization, and uptime.
- Memory page reads real workspace memory files instead of using a separate database.
- Mission-control uptime is now boot-persistent through the stable 4180 runtime path.
- Current notable open issue: the site works, but the UI still needs more visual polish to feel elegant rather than clunky.

## Operating rules for continuity

- For each meaningful message from haolun: identify the implied task/follow-up, create or update it in the mission-control task board, and keep the lane marking current.
- Run a full memory optimization + task board update roughly hourly while actively working: capture meaningful changes from the last hour, record passive work like push IDs, reread curated memory + today's note for accuracy, tighten stale task/event state, and lightly optimize today's memory without rewriting prior daily files.
- Keep the local mission-control site up while hazoc is actively running.
- Push meaningful workspace changes to GitHub once per hour while active, aligned to `:30`.
- A visible recurring duty does not count as done by itself; it only counts after a real commit/push or a verified clean/no-change check.

## Default memory workflow

- Use retrieval first: search memory for relevant prior context before answering new meaningful questions.
- Load only the useful pieces.
- After answering, store the durable result and avoid carrying excess context forward.
- Default continuity stack: `memory/active-state.md` + mission-control task board + `memory/YYYY-MM-DD.md` + curated memory files.

## Skills and workflow defaults

- `grounded-evolver` is the default self-improvement / evolution framework.
- Supporting modules: `workspace-continuity`, `workspace-memory-stack`, `workspace-graph`, and `safe-evolution-loop`.
- For YouTube/video links, use `youtube-watcher` and `video-frames` together by default.

## Channel rules

- Discord, especially `#control-center`, is an extension channel, not a separate working self.
- Telegram DMs are also an extension channel.
- Important requests, decisions, and follow-ups from those channels must be mirrored back into the mission-control task board and workspace memory.

## Tooling state worth remembering

- The `gog` skill and CLI are installed and authenticated for Google Workspace use.
- Gmail, Calendar, Drive, and Contacts access were verified after the required Google APIs were enabled.

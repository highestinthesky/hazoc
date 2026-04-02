# Product Direction Reference

This file holds detailed product/context direction that should stay durable but does not need to sit in the always-injected startup prompt every turn.

## Mission-control direction

- Mission control is the shared workspace between haolun and hazoc.
- The important surfaces are: task tracking, hazoc's planned schedule, memory/journal, and end-of-session continuity.
- The shared space should preserve continuity across resets and prioritize durable state over chat-only memory.
- The build should start local-only, but the architecture should be ready to become LAN-accessible later without a rewrite.

## Schedule / events direction

- The schedule/calendar should stay grounded in mission-control state rather than defaulting to Google Calendar as the primary source of truth.
- User-entered scheduled events should stay separate from hazoc work tasks.
- Schedule uses America/New_York and is event-first, with scheduled tasks shown separately from user events.
- The Schedule page includes a text box that sends directly to hazoc for schedule requests, with inline hazoc replies for confirmations and clarifying questions.
- Planned schedule-user model: 4 schedule profiles total — hazoc, haolun, and two additional users.
- Planned request structure: a schedule request may specify an event name, time, and optionally ask for the event to also be added to another user's schedule.
- Planned integrations: link the user profiles to Google Calendar and let hazoc send reminders to each user through Discord and/or Telegram.

## Current mission-control state

- Reliable local URL: `http://127.0.0.1:4180/`.
- The site currently has Tasks, Protocol, Schedule, Events, Memory, and Skills pages.
- Tasks are stored locally and act as shared project memory.
- The current Tasks page uses three practical sections: Workbench, On Hold, and Archived.
- Workbench is meant for active project work only; standing rules and recurring duties live in Protocol.
- Scheduled events are stored separately from tasks in a dedicated events store and can be organized/archived on the Events page.
- Memory page reads real workspace memory files instead of using a separate database.
- Mission-control uptime is boot-persistent through the stable 4180 runtime path.
- Current notable open issue: the site works, but the UI still needs more visual polish to feel elegant rather than clunky.

## Skills / UI direction

- The Skills page should use concise summaries of how skills work rather than authored flowcharts; the chart-heavy direction was dropped after costing too much time for too little value.
- Diagram default when authoring flowcharts/skill graphs: orthogonal connectors with rounded corners and at most one turn per arrow unless there is a strong reason otherwise.
- Visible UI fixes count only when the rendered result visibly addresses the complaint.

## Market-moving news digest direction

- Preferred market-monitoring direction is not ticker-specific watchlists first.
- Instead, the desired system should gather major public market-moving headlines, infer which sectors and important stocks are likely affected, and compile those into digest summaries.
- The digest should emphasize why the headline matters, likely affected names/ETFs/sectors, and whether the impact is broad-market, sector-specific, or single-name.
- Default source classes should stay public and bounded: news aggregators/RSS, financial news pages, official macro/government releases, SEC/company IR releases, and public market-data pages.
- Avoid private logins, cookie harvesting, paywalled scraping, and sketchy rumor sources by default.
- Delivery should happen at configurable intervals rather than as open-ended autonomous roaming.

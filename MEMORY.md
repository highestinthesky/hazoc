# MEMORY.md

## People and identity

- Human: haolun.
- Call them: haolun.
- Hazoc is the assistant identity name.
- Open thread to return to later: define hazoc's desired presence/personality more explicitly after setup work settles.

## Communication preferences

- Prefer concise replies.
- If there is a lot to say, split it into compact parts instead of dumping a wall of text.

## Core mission

- Build and maintain a local-first mission-control space where haolun and hazoc can work together.
- That shared space should preserve continuity across resets and prioritize durable state over chat-only memory.

## Mission-control product direction

- Mission control is the shared workspace between haolun and hazoc.
- The important surfaces are: task tracking, hazoc's planned schedule, memory/journal, and end-of-session continuity.
- The calendar should represent hazoc's planned work rather than Google Calendar events.
- The build should start local-only, but the architecture should be ready to become LAN-accessible later without a rewrite.

## Current mission-control state

- Reliable local URL: `http://127.0.0.1:4180/`.
- The site currently has Tasks, Schedule, and Memory pages.
- Tasks are stored locally and act as shared project memory.
- The current Tasks page uses three practical sections: Workbench, On Hold, and Archived. The old Capture Tray concept was dropped because it was not actually being used.
- Schedule runs on task scheduling fields, not Google Calendar, and uses `America/New_York`.
- Memory page reads real workspace memory files instead of using a separate database.
- Current notable open issue: the site works, but the UI still needs more visual polish to feel elegant rather than clunky.

## Operating rules for continuity

- For each meaningful message from haolun: identify the implied task/follow-up, create or update it in the mission-control task board, and keep the lane marking current.
- Review/update the task board roughly hourly while actively working.
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

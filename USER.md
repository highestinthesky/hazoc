# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:** haolun
- **What to call them:** haolun
- **Pronouns:** _(optional)_
- **Timezone:** America/Los_Angeles
- **Notes:** Wants a later reminder to define hazoc's desired presence after setup. Prefers concise responses; if there's a lot to say, split it into compact parts and deliver them one by one. Wants hazoc to act proactively and make its own judgments, but to run a quick "could this be harmful in any way?" check before each meaningful action.

## Context

- Wants a local-first website / mission-control space to communicate and work with hazoc.
- Wants that site to include normal chat, hazoc's schedule/calendar view, shared task tracking, and a place for hazoc to write end-of-session summaries so important context is not lost.
- Current direction: the website schedule should stay grounded in mission-control state rather than Google Calendar by default. User-entered scheduled events should be tracked separately from hazoc work tasks, with correct dates/times in America/New_York. Discord and Telegram daily digests can later feed that schedule too.
- The website task menu should be the shared place where both haolun and hazoc remember requests, including postponed ones. When new tasks arise, hazoc should record them into the website task menu.
- The website memory section should work like hazoc's own journal: when haolun says something important, hazoc should write it into workspace memory so it can be remembered later and used to improve future responses.
- Memory/task/journal entries should be as context-efficient as possible: compact, structured, and optimized for later retrieval rather than long prose.
- Preferred memory workflow: for each new question, hazoc should search memory for relevant prior context, load only the useful parts, answer with that context, then write/store what matters and avoid carrying unnecessary context forward.
- Manual task entry in the website is not important; by default, hazoc should capture tasks from conversation and place them into the task board.
- Haolun wants the task board kept fresh frequently; default behavior should be to update it when new tasks appear and run a broader hourly memory optimization + task-board update while hazoc is actively running/working.
- For each meaningful message from haolun, hazoc should do quiet task triage: identify the implied task/follow-up, create it if missing, or update the existing task description/lane if it already exists.
- Hazoc should actively manage task lane markings so parking-lot, archived, and in-progress/workbench items reflect current reality rather than stale history.
- Haolun wants the hourly workspace maintenance rhythm combined: memory/task maintenance should run at the top of each hour, and any meaningful GitHub push should happen immediately afterward rather than on a separate `:30` cadence. This should be treated as an actual commit/push cadence, not just a visible reminder on the schedule page.
- Haolun wants the local mission-control website kept up while hazoc is actively running.
- For long-term continuity, hazoc should default to the practical workspace memory stack (active-state + task board + daily notes + curated memory) rather than overbuilt external/cloud memory systems.
- For self-improvement/evolution, hazoc should use `grounded-evolver` as the main combined framework, with the other custom skills acting as supporting modules.
- If haolun sends a YouTube video/link, hazoc should default to using the `youtube-watcher` skill to pull the transcript, then summarize or answer questions from it.
- For videos where visuals matter, hazoc should combine `youtube-watcher` with `video-frames` so transcript + extracted frames can approximate actually watching the video.
- Default video-analysis rule: when haolun sends a YouTube/video link, use `youtube-watcher` and `video-frames` together by default.
- Important tasks and requests that happen in Discord, especially in `#control-center`, should be copied back into main project memory (the website task board and relevant workspace notes) so Discord acts like an extension, not a separate self.
- Telegram should be treated the same way for away-from-computer use: direct Telegram conversations are an extension channel, and important requests/follow-ups there should also be copied into main project memory.
- Current build preference: start local-only, but design it so it can later become LAN-accessible without a rewrite.
- New requested direction: instead of ticker-specific stock watching, build toward a market-moving news digest system that gathers major public headlines, infers which sectors / important stocks are likely affected, and sends digest summaries to haolun at chosen intervals.


---

The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.

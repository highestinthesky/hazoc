# Session: 2026-04-09 22:44:49 UTC

- **Session Key**: agent:main:main
- **Session ID**: 537e17d6-685d-431e-a6f7-6c1d2b6a95dc
- **Source**: webchat

## Conversation Summary

assistant: [[reply_to_current]] Bluntly: for these files, there are only **2 real levers**:

1. **fewer always-loaded files**
2. **shorter always-loaded files**

Searching better does **not** reduce this fixed per-request tax.

**Best cut plan**
- **`AGENTS.md`** → shrink to only:
  - startup order
  - red lines
  - retrieval-first rule
  - subagent/worker identity rule
- **`SOUL.md` + `IDENTITY.md`** → merge; keep persona only
- **`USER.md`** → stable preferences only
- **`MEMORY.md`** → durable facts only; remove workflow/rule duplicates
- **`TOOLS.md`** → true machine-specific notes only; strip reminders/routing prose
- **`HEARTBEAT.md`** → keep empty unless actively needed
- **`memory/active-state.md`** → tiny live anchor, not a mini-log

**Rule for anything that isn’t startup-critical**
- move it out of root files
- put it in:
  - `PROTOCOL_SPINE.md`
  - `RECALL_MAP.md`
  - references/
  - task memory
  - worker/namecard bundles
- then retrieve it only on trigger

**Practical target**
- current workspace project-context tax is roughly **~6k tokens**
- I’d try to cut that to more like **~2k or less**

**Even better, if platform-configurable later**
- auto-inject only the true core
- make everything else recall-only or actor-local

So the real move is:
**treat root files like boot ROM: tiny, dense, no examples, no duplicates, no history.**

That also matches the earlier design direction: only the identity/operating core plus a tiny live anchor should always load; tasks, notes, and deep refs stay recall-only. Source: memory/2026-04-02.md#L23-L25
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Thu 2026-04-09 17:59 EDT] yes, I like that idea. however, run tests while implementing to guarantee that nothing goes wrong
assistant: I’m going to do this as a rollbackable migration, not a blind trim: first inventory the startup-critical rules, then shrink one file at a time and run coverage checks after each step.
assistant: I’m measuring the current prompt surface first so I can show the before/after deltas, then I’ll add a coverage test harness before trimming.
assistant: I’m adding a machine-checkable coverage/budget test so this doesn’t rely on “looks fine to me.” Then I’ll trim root files first, run root-only tests, trim startup files, and run the full pass.
assistant: The harness is in place. I’m running it against the current files first so we have a baseline failure report before trimming.
assistant: Root files are trimmed. I hit a harmless tool quirk on making `HEARTBEAT.md` fully empty, so I’m setting it to a single newline and then running the root-only checks.
assistant: One tiny cleanup left: making `HEARTBEAT.md` truly empty, then rerunning the root suite.
assistant: Startup files are trimmed. Now I’m running the startup-only suite and then the full combined suite.
assistant: I’ve got a clean pass. I’m just writing the result back into daily/task memory so the next session doesn’t have to reverse-engineer what changed.
assistant: [[reply_to_current]] Done — and I tested it as I went.

What I changed:
- added a rollback snapshot before edits
- added a machine-checkable harness:
  - `mission-control/data/prompt-surface-spec.json`
  - `scripts/validate_prompt_surface.py`
- slimmed the root/startup files into boot-ROM style:
  - `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `TOOLS.md`, `MEMORY.md`
  - `PROTOCOL_SPINE.md`, `RECALL_MAP.md`, `memory/active-state.md`

Test status:
- `--scope root` → PASS
- `--scope startup` → PASS
- `--scope all` → PASS

Size delta:
- root files: **20100 → 5037 chars**
- startup files: **10419 → 4608 chars**
- combined: **30519 → 9645 chars**  
  so roughly a **68% reduction**

Important caveat:
- this helps **new/fresh sessions** the most
- the **current** thread still carries some older already-loaded context until reset/compaction

And yes: I changed `SOUL.md` too, so I’m telling you explicitly.

If you want, next I can do one of two things:
1. give you a **diff-style summary** of exactly what got removed/moved, or  
2. keep going and do a **second slimming pass** on anything still not startup-critical.
user: Pre-compaction memory flush. Store durable memories only in memory/2026-04-09.md (append only). Treat MEMORY.md, SOUL.md, TOOLS.md, and AGENTS.md as read-only during this flush; never overwrite or replace them. Do not create timestamped variant files. Reply with NO_REPLY if nothing durable needs to be stored.

Store durable memories only in memory/2026-04-09.md (create memory/ if needed).

If memory/2026-04-09.md already exists, APPEND new content only and do not overwrite existing entries.

Treat workspace bootstrap/reference files such as MEMORY.md, SOUL.md, TOOLS.md, and AGENTS.md as read-only during this flush; never overwrite, replace, or edit them.
Current time: Thursday, April 9th, 2026 — 6:43 PM (America/New_York) / 2026-04-09 22:43 UTC
assistant: NO_REPLY
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Thu 2026-04-09 18:43 EDT] alright, do you want to restart this session so that the new benefits kick into action?
assistant: [[reply_to_current]] Yeah — a fresh session is the cleanest way to actually cash in the slimmer prompt surface. This thread is still carrying some old context mass, so if you reset now, I should wake up lighter and re-anchor from the new boot-ROM files.

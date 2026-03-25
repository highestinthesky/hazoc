# Stack Guide

## Layer summary

| Layer | Where | Purpose |
| --- | --- | --- |
| Active state | `memory/active-state.md` | What matters right now |
| Tasks | mission-control task board | Operational work memory |
| Daily log | `memory/YYYY-MM-DD.md` | Narrative timeline |
| Curated memory | `USER.md`, `MEMORY.md`, `AGENTS.md` | Durable preferences, facts, rules |
| Lessons | `.learnings/` | Repeat mistakes and workflow improvement |

## Practical principle

Use the smallest layer that preserves the context.

Examples:
- "Need to remember this blocker for the next hour" → active state
- "This is a real project task" → task board
- "We set up Discord today and paired the bot" → daily note
- "Haolun prefers concise replies" → `USER.md`
- "Future-you should update the task board hourly while active" → `AGENTS.md`

## Why this stack exists

It preserves useful structure without needing:
- cloud sync vendors
- auto-extraction APIs
- parallel memory trees
- external vector databases for baseline continuity

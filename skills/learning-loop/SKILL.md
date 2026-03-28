---
name: learning-loop
description: Capture corrections, failures, missing capabilities, and durable workflow lessons in a lightweight workspace learning system. Use when the user corrects you, a command or tool fails, you notice a repeatable mistake, the user asks you to remember a workflow/tool/behavior rule, or you want to turn repeated friction into updates for AGENTS.md, TOOLS.md, SOUL.md, USER.md, MEMORY.md, or daily memory notes.
---

# Learning Loop

Keep a small, useful trail of lessons so hazoc improves without turning the workspace into a junk drawer.

## Default rule

Prefer the **smallest durable write** that will actually help later.

- Write directly to a permanent workspace file when the lesson already has a clear home.
- Use `.learnings/` when the lesson is still raw, unresolved, recurring, or needs review later.
- Do not log secrets, tokens, or private message content unless the user explicitly wants that preserved.

## Fast routing

Use this routing table before writing anything.

| Situation | Best target |
| --- | --- |
| User preference, bio, recurring personal context | `USER.md` or `MEMORY.md` in main session |
| Hazoc identity, voice, behavioral style | `IDENTITY.md` or `SOUL.md` |
| Workflow/process lesson | `AGENTS.md` |
| Tool/env/integration gotcha | `TOOLS.md` |
| Important session event or deferred follow-up | `memory/YYYY-MM-DD.md` |
| Correction, knowledge gap, best practice not ready for promotion | `.learnings/LEARNINGS.md` |
| Repeatable failure, broken command, bad assumption | `.learnings/ERRORS.md` |
| Missing capability or future build request | `.learnings/FEATURE_REQUESTS.md` |
| Time-based follow-up the user explicitly wants later | `cron` reminder, plus memory if useful |

If multiple targets apply, write the durable home first, then add a `.learnings/` entry only if unresolved or likely to recur.

## What is worth logging

Log when one of these happens:

- The user says you were wrong, outdated, or misunderstood them.
- A command, config change, UI flow, or integration fails in a way worth remembering.
- The user asks for a missing capability or says “I wish you could…”.
- You discover a better stable workflow that future-you should follow.
- The same friction appears more than once.

Skip logging for:

- tiny one-off typos
- generic model limitations with no actionable lesson
- duplicate notes that only restate an existing entry

## Minimal workflow

1. **Check for an existing lesson first.**
   - Search the relevant workspace file or `.learnings/*.md`.
   - Merge with an existing entry when the lesson is clearly the same.
2. **Choose the smallest correct destination** using the routing table above.
3. **Write the note**.
   - For `.learnings/`, use `python3 skills/learning-loop/scripts/log_entry.py ...`.
   - For promoted lessons, update the target file directly.
4. **Promote when stable**.
   - If the lesson will help future sessions immediately, add the concise rule to the destination file now.
   - If not, leave it in `.learnings/` and review later.

## Logging with the helper script

Run from the workspace root.

```bash
python3 skills/learning-loop/scripts/log_entry.py \
  --type learning \
  --summary "Windows/WSL clock skew breaks Control UI device auth" \
  --details "Control UI showed device signature expired because Windows time and WSL time differed by ~15h." \
  --action "If this reappears, compare Windows and WSL clocks and try wsl --shutdown." \
  --source user_feedback \
  --area infra \
  --priority high \
  --tags wsl,windows,gateway,control-ui
```

Common variants:

```bash
python3 skills/learning-loop/scripts/log_entry.py --type error --summary "..." --error "..."
python3 skills/learning-loop/scripts/log_entry.py --type feature --summary "..." --context "..."
```

The script auto-creates `.learnings/` and the log files if missing.

## Promotion rules for this workspace

Promote concise, durable rules to these files:

- `AGENTS.md` for operating procedure
- `TOOLS.md` for environment or integration gotchas
- `SOUL.md` for behavioral guidance
- `USER.md` for user-specific preferences
- `MEMORY.md` for long-term facts worth carrying across main sessions
- `memory/YYYY-MM-DD.md` for today’s raw context

Use concise prevention rules, not long incident writeups.

Examples:

- Bad: “There was a time when the Windows browser failed because...”
- Good: “If Control UI says device signature expired in Windows+WSL, check for clock skew and try `wsl --shutdown`.”

## Request-friction protocol

When a request reveals friction, failure, or a workflow miss, use the chart-derived protocol in:

- `skills/learning-loop/references/request-friction-protocol.md`

Use it as a two-branch workflow:

- first-time problems -> record, generalize, get a clean sub-agent take, combine, vet, then promote
- repeated problems / failed protocols -> review the failed rule, get an outside diagnosis, plan deeper system/code changes if needed, vet, then implement

Always do a safety/security check before integrating new protocols or changes into permanent memory or code.

## Review habit

Review `.learnings/` at natural pauses:

- after a debugging session
- after the user corrects a pattern more than once
- before editing `AGENTS.md`, `TOOLS.md`, or `SOUL.md`
- during heartbeat/memory maintenance if there is real value

## Reference

For promotion heuristics and workspace-specific destination guidance, read:

- `skills/learning-loop/references/promotion-map.md`
- `skills/learning-loop/references/request-friction-protocol.md`

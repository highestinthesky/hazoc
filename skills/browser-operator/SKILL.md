---
name: browser-operator
description: Drive a real browser for dynamic websites, login-gated apps, dashboards, forms, clicks, screenshots, and workflows that need JavaScript or page interaction. Use when `web_fetch` or normal web search is not enough because the page must be clicked, typed into, waited on, authenticated, or visually inspected. Do not use for simple public web search, quick factual lookups, or plain article reading.
metadata: {"openclaw":{"emoji":"🌐","homepage":"https://clawhub.ai/thesethrose/agent-browser","requires":{"bins":["agent-browser"]}}}
---

# Browser Operator

Use `agent-browser` only when a **real browser session** gives clear value.

## Prefer simpler tools first

Before using this skill, ask:

- Can `web_search` answer this directly?
- Can `web_fetch` read the page without interaction?
- Is the user asking for research rather than website operation?

If yes, do **not** use this skill.

Good fits:

- login-gated sites
- JavaScript-heavy dashboards
- clicking through filters, tabs, and modals
- filling forms
- taking screenshots or PDFs
- inspecting what is visibly on the page

## Core loop

Most tasks should follow this loop:

1. Open the page.
2. Snapshot interactive elements.
3. Interact using element refs.
4. Wait for navigation or content changes.
5. Snapshot again after meaningful DOM changes.
6. Extract the needed result, screenshot, or final state.

Minimal command pattern:

```bash
agent-browser open <url>
agent-browser snapshot -i
agent-browser click @e1
agent-browser wait --load networkidle
agent-browser snapshot -i
```

## Best-practice defaults

- Use `snapshot -i` first; it is usually the most useful view.
- Re-snapshot after navigation, modal opens, or large UI changes.
- Use `fill` instead of `type` when replacing existing input values.
- Use `wait --url`, `wait --text`, or `wait --load networkidle` instead of blind sleeps when possible.
- Use `--headed` only when debugging or when visual confirmation matters.
- Use `--session <name>` for parallel or long-lived browser sessions.

## Authentication and state

For sites you may revisit in the same task or later:

```bash
agent-browser state save auth.json
agent-browser state load auth.json
```

Treat saved state files as sensitive. Do not expose their contents in chat.

## Safety and privacy

- Ask before performing meaningful external side effects unless the user clearly requested them.
  - examples: submitting a real form, placing an order, posting content, sending messages
- Do not paste or echo secrets back into chat unless needed.
- Prefer screenshots or concise summaries over dumping full page HTML.

## Useful commands

- Open / navigate: `open`, `back`, `forward`, `reload`
- Inspect: `snapshot -i`, `get text`, `get url`, `get title`
- Interact: `click`, `fill`, `type`, `press`, `select`, `check`
- Wait: `wait --url`, `wait --text`, `wait --load networkidle`
- Output: `screenshot`, `pdf`
- Debug: `--headed`, `console`, `errors`, `highlight`

## Troubleshooting

- Element missing: re-run `snapshot -i`; refs change after navigation.
- Page not stable: use a real wait condition before interacting again.
- Wrong element: scope with better page state, then snapshot again.
- Need a visible sanity check: run with `--headed`.

## Reference

For command recipes, read `{baseDir}/references/recipes.md`.

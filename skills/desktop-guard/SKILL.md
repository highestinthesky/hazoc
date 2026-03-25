---
name: desktop-guard
description: Guarded local desktop automation for explicit mouse, keyboard, screenshot, window, and clipboard tasks. Use only when someone directly asks for desktop control on a GUI machine and you want a safer posture than a fully autonomous desktop agent.
---

# Desktop Guard

## Overview

Desktop Guard is my safer fork of the upstream desktop-control idea. It keeps the useful local control primitives, but strips out the autonomous agent layer and defaults mutating actions to guarded execution so desktop control is deliberate instead of slippery.

## When to use this skill

Use this skill when the request is explicitly about:
- moving or clicking the mouse
- typing text or pressing keys in a local GUI
- taking screenshots
- checking window titles
- reading or setting clipboard text

Do **not** use this skill when:
- the user has not clearly asked for desktop control
- the environment is headless / server-only
- a safer first-class tool already exists
- the action would be surprising, destructive, or privacy-sensitive without confirmation

## Quick start

### Safe inspection actions

```bash
python3 {baseDir}/scripts/desktop_guard.py position
python3 {baseDir}/scripts/desktop_guard.py windows
python3 {baseDir}/scripts/desktop_guard.py screenshot --output /tmp/desktop-guard.png
python3 {baseDir}/scripts/desktop_guard.py clipboard-get
```

### Mutating actions require `--live`

```bash
python3 {baseDir}/scripts/desktop_guard.py move 800 500 --live
python3 {baseDir}/scripts/desktop_guard.py click --x 800 --y 500 --live
python3 {baseDir}/scripts/desktop_guard.py type "hello world" --live
python3 {baseDir}/scripts/desktop_guard.py hotkey ctrl s --live
python3 {baseDir}/scripts/desktop_guard.py clipboard-set "draft text" --live
```

Without `--live`, mutating commands return a dry-run preview only.

## Workflow

### A. Inspect first

Before clicking/typing, prefer one or more of:
- `position`
- `windows`
- `screenshot`

### B. Mutate only with explicit user intent

Use `--live` only when the user actually wants the action performed.

### C. Keep actions small

Prefer short, checkable steps over long autonomous sequences.

Good:
- move
- click
- type one string
- save with one hotkey

Bad:
- opaque multi-minute autonomous workflows
- uncontrolled loops
- silent screenshot harvesting

## Safety posture

- No autonomous AI desktop agent.
- No network calls.
- Mutating commands are dry-run by default.
- Still powerful: screenshots and clipboard can expose sensitive data, so use carefully.

## Resources

### scripts/
- `desktop_guard.py` — guarded CLI for local desktop control

### references/
- `vetting.md` — upstream review + fork rationale
- `safety.md` — operational guardrails for future use

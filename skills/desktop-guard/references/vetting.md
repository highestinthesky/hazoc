# Upstream vetting summary

## Reviewed source skill

- `matagul/desktop-control`

## Assessment

Risk: **medium**

Why:
- the skill appears honest about what it does
- no obvious credential grab or network exfiltration showed up in the reviewed files
- but it is inherently powerful: mouse/keyboard control, screenshots, window state, and clipboard access can expose sensitive data or perform real actions on the machine
- the upstream package also includes an `AIDesktopAgent` layer, which increases autonomy/risk beyond simple local control primitives

## What I kept conceptually

- direct desktop primitives
- screenshot / window / clipboard support
- failsafe mindset

## What I rejected

- the autonomous `AIDesktopAgent`
- default-to-live mutation posture
- broad marketing claims about being the "most advanced" or fully autonomous

## Fork design choice

`desktop-guard` is intentionally narrower:
- explicit CLI primitives only
- mutating commands require `--live`
- no autonomous planning layer
- no network behavior

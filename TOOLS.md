# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## OpenClaw reminders

- For **visible timed pings in a chat/channel**, do not rely on a `cron` job that only injects a main-session `systemEvent`; that can wake the agent with an internal reminder without guaranteeing a surfaced channel message.
- Prefer a reminder path with explicit chat delivery / announce behavior when the user asked to be pinged in-channel.

## Discord routing

- Main task-completion pings currently use explicit Discord announce delivery to: `hzwp / #main_updates` (`1487645227421536327`)
- That route was live-tested successfully on 2026-03-28.
- Current fallback channel remains available: `hzwp / #control-center` (`1485016833819021495`)
- Haolun mention format for completion pings: `<@1049450008505757706>`
- Canonical behavior/settings file: `mission-control/data/notifications.json`

---

Add whatever helps you do your job. This is your cheat sheet.

# Agent namecards

Use this directory for **durable long-lived agent/channel identities**.

These are not extra souls. They are compact role cards for identities that repeatedly wake in the same place and need stable jurisdiction, reporting lines, and memory boundaries.

Good fit:
- main direct session
- long-lived Discord control channel agent
- separate sandbox agents like `guest-safe-web`

Bad fit:
- throwaway cron runs
- disposable research/outside-review helpers
- one-off subagents

## Shape

```text
agent-namecards/<card-id>/
  namecard.json   # durable role card
  state.json      # optional local state/checkpoint for that identity
```

## What belongs here

- display name
- stable session identity / mapping
- role / jurisdiction
- reporting lines
- memory boundaries
- wake reminder / re-anchor note

## What does not belong here

- personality bloat
- a second memory system duplicating workspace memory
- sensitive secrets

Think **nametag + clipboard**, not a second soul.

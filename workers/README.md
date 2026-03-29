# Managed workers

Use this directory only for **recurring or restart-sensitive background workers**.

Do **not** force one-off research/disposable subagents into this pattern.

## Shape

Each managed worker gets its own folder:

```text
workers/<worker-id>/
  spec.json   # read-only identity, purpose, wake contract, commands
  state.json  # writable checkpoint / last wake metadata
```

## Contract

Every managed wake message should include:

1. the exact `worker-id`
2. the exact bootstrap command
3. an instruction to read the worker bundle before acting

Recommended bootstrap helper:

```bash
python3 scripts/bootstrap_worker.py --worker-id <worker-id> --json
```

The worker should treat the spec/state files as authoritative for purpose and current checkpoint instead of relying on vague session memory.

## When to use

Good fit:
- recovery dispatchers
- scheduled monitors
- recurring digests
- restart-sensitive background jobs

Bad fit:
- disposable outside reviews
- one-shot research helpers
- short-lived task subagents with no durable wake cycle

# Helper workflows

Use these helpers when grounded-evolver needs more operational leverage than a raw planner output.

## `scripts/prepare_outside_review.py`

Use when:
- `grounded_evolve.py` says outside review is required
- you want one reusable way to turn planner JSON into the exact clean-room spawn payload
- you want a built-in fallback from `sandbox=require` to `sandbox=inherit` when the runtime rejects the stricter spawn

Typical use:

```bash
python3 skills/grounded-evolver/scripts/grounded_evolve.py ... --json > /tmp/grounded-plan.json
python3 skills/grounded-evolver/scripts/prepare_outside_review.py --plan-file /tmp/grounded-plan.json --json
```

What it gives you:
- `preferredSpawn` -> exact payload for `sessions_spawn`
- `fallbackSpawn` -> same payload but with `sandbox=inherit`
- the exact task text from the planner
- the clean-room notes in one place

## `scripts/snapshot_revert.py`

Use when:
- a protocol, workflow, rule, or helper patch needs a reversible pre-change snapshot
- you want something cheaper and more reliable than manual copy/paste backups
- you need to restore the exact prior file contents after failed vetting or validation

Typical use:

```bash
python3 skills/grounded-evolver/scripts/snapshot_revert.py snapshot \
  --name discord-closeout-repair \
  --file AGENTS.md \
  --file mission-control/data/notifications.json \
  --note "Before revising the closeout gate"

# ...make and test the change...

python3 skills/grounded-evolver/scripts/snapshot_revert.py restore \
  --name discord-closeout-repair
```

Notes:
- snapshots live under `.learnings/snapshots/`
- file paths are stored workspace-relative for easy review
- missing files are tracked too, so restoring can delete newly created files when needed
- this helper snapshots whole files, not ASTs or semantic patches; keep edits surgical anyway

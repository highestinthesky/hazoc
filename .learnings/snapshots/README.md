# Local snapshots

This directory is for **local-only reversible backups** created during risky or structural edits.

Examples:
- pre-change whole-file snapshots from `skills/grounded-evolver/scripts/snapshot_revert.py`
- temporary exported session-store backups before cleanup or rename sweeps
- cron/session backup exports before deleting stale runtime rows

## Policy

- Keep the directory itself in Git so the pattern is visible.
- Do **not** commit the generated snapshot JSON files.
- Snapshot JSONs are ignored by `.gitignore` on purpose because they are:
  - generated
  - noisy
  - sometimes large
  - sometimes privacy-sensitive

## Typical flow

1. Create a snapshot before a risky change.
2. Validate the change.
3. Keep the snapshot locally for a while if rollback might still matter.
4. Delete old snapshots once the change is clearly stable.

Think of this folder as a local safety net, not durable project history.

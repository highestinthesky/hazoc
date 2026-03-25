#!/usr/bin/env python3
"""Append structured entries to workspace .learnings markdown logs."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
from pathlib import Path

ROOT = Path.cwd()
LEARNINGS_DIR = ROOT / ".learnings"
FILES = {
    "learning": LEARNINGS_DIR / "LEARNINGS.md",
    "error": LEARNINGS_DIR / "ERRORS.md",
    "feature": LEARNINGS_DIR / "FEATURE_REQUESTS.md",
}
PREFIX = {"learning": "LRN", "error": "ERR", "feature": "FEAT"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--type", choices=FILES.keys(), required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--details", default="")
    p.add_argument("--action", default="")
    p.add_argument("--error", default="")
    p.add_argument("--context", default="")
    p.add_argument("--source", default="conversation")
    p.add_argument("--area", default="general")
    p.add_argument("--priority", default="medium")
    p.add_argument("--status", default="pending")
    p.add_argument("--tags", default="")
    p.add_argument("--related-files", default="")
    p.add_argument("--see-also", default="")
    p.add_argument("--complexity", default="medium")
    p.add_argument("--frequency", default="first_time")
    p.add_argument("--root", default=str(ROOT))
    return p.parse_args()


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:48] or "entry"


def ensure_file(path: Path, entry_type: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    title = {
        "learning": "# Learnings\n\nRaw lessons, corrections, and best practices that are not yet promoted.\n",
        "error": "# Errors\n\nRepeatable failures, broken commands, and debugging notes worth remembering.\n",
        "feature": "# Feature Requests\n\nUser-requested capabilities and deferred build ideas.\n",
    }[entry_type]
    path.write_text(title + "\n", encoding="utf-8")


def next_id(path: Path, prefix: str, day: str) -> str:
    if not path.exists():
        return f"{prefix}-{day}-001"
    text = path.read_text(encoding="utf-8")
    matches = re.findall(rf"{re.escape(prefix)}-{day}-(\d{{3}})", text)
    n = max((int(m) for m in matches), default=0) + 1
    return f"{prefix}-{day}-{n:03d}"


def bullet_value(raw: str) -> str:
    values = [part.strip() for part in raw.split(",") if part.strip()]
    return ", ".join(values) if values else "none"


def build_entry(args: argparse.Namespace, entry_id: str, now: dt.datetime) -> str:
    tags = bullet_value(args.tags)
    related_files = bullet_value(args.related_files)
    see_also = args.see_also.strip() or "none"
    summary = args.summary.strip()
    if args.type == "learning":
        details = args.details.strip() or summary
        action = args.action.strip() or "Promote or revisit if this recurs."
        return f"""
## [{entry_id}] {slugify(summary)}

**Logged**: {now.isoformat()}
**Priority**: {args.priority}
**Status**: {args.status}
**Area**: {args.area}

### Summary
{summary}

### Details
{details}

### Suggested Action
{action}

### Metadata
- Source: {args.source}
- Related Files: {related_files}
- Tags: {tags}
- See Also: {see_also}

---
""".lstrip()
    if args.type == "error":
        error_text = args.error.strip() or summary
        context = args.context.strip() or args.details.strip() or "No extra context recorded."
        fix = args.action.strip() or "Investigate and document the stable fix if found."
        return f"""
## [{entry_id}] {slugify(summary)}

**Logged**: {now.isoformat()}
**Priority**: {args.priority}
**Status**: {args.status}
**Area**: {args.area}

### Summary
{summary}

### Error
{error_text}

### Context
{context}

### Suggested Fix
{fix}

### Metadata
- Source: {args.source}
- Related Files: {related_files}
- Tags: {tags}
- See Also: {see_also}

---
""".lstrip()

    context = args.context.strip() or args.details.strip() or "No extra context recorded."
    action = args.action.strip() or "Define scope and revisit when this becomes active work."
    return f"""
## [{entry_id}] {slugify(summary)}

**Logged**: {now.isoformat()}
**Priority**: {args.priority}
**Status**: {args.status}
**Area**: {args.area}

### Requested Capability
{summary}

### User Context
{context}

### Complexity Estimate
{args.complexity}

### Suggested Implementation
{action}

### Metadata
- Source: {args.source}
- Frequency: {args.frequency}
- Related Files: {related_files}
- Tags: {tags}
- See Also: {see_also}

---
""".lstrip()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")

    global ROOT, LEARNINGS_DIR, FILES
    ROOT = root
    LEARNINGS_DIR = ROOT / ".learnings"
    FILES = {
        "learning": LEARNINGS_DIR / "LEARNINGS.md",
        "error": LEARNINGS_DIR / "ERRORS.md",
        "feature": LEARNINGS_DIR / "FEATURE_REQUESTS.md",
    }

    target = FILES[args.type]
    ensure_file(target, args.type)

    now = dt.datetime.now().astimezone().replace(microsecond=0)
    day = now.strftime("%Y%m%d")
    entry_id = next_id(target, PREFIX[args.type], day)
    entry = build_entry(args, entry_id, now)

    with target.open("a", encoding="utf-8") as fh:
        if target.stat().st_size > 0:
            fh.write("\n")
        fh.write(entry)

    print(f"Appended {entry_id} to {os.path.relpath(target, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

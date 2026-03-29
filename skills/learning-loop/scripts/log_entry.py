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
STATIC_FILES = {
    "learning": LEARNINGS_DIR / "LEARNINGS.md",
    "feature": LEARNINGS_DIR / "FEATURE_REQUESTS.md",
}
ERROR_INDEX = LEARNINGS_DIR / "errors.md"
ERROR_DIR = LEARNINGS_DIR / "errors"
PREFIX = {"learning": "LRN", "error": "ERR", "feature": "FEAT"}
DAY_HEADING_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--type", choices=["learning", "error", "feature"], required=True)
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
    p.add_argument("--logged-at", default="")
    p.add_argument("--root", default=str(ROOT))
    return p.parse_args()


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:48] or "entry"


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def parse_logged_at(raw: str) -> dt.datetime:
    if not raw.strip():
        return dt.datetime.now().astimezone().replace(microsecond=0)

    value = raw.strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid --logged-at value: {raw}") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.datetime.now().astimezone().tzinfo)
    return parsed.astimezone().replace(microsecond=0)


def bullet_value(raw: str) -> str:
    values = [part.strip() for part in raw.split(",") if part.strip()]
    return ", ".join(values) if values else "none"


def ensure_regular_file(path: Path, entry_type: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    title = {
        "learning": "# Learnings\n\nRaw lessons, corrections, and best practices that are not yet promoted.\n",
        "feature": "# Feature Requests\n\nUser-requested capabilities and deferred build ideas.\n",
    }[entry_type]
    path.write_text(title + "\n", encoding="utf-8")


def ensure_errors_index(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(
        "# errors\n\n"
        "Compact landing page for repeatable failures, broken workflows, and debugging notes.\n\n"
        "## Structure\n\n"
        "- keep the index file short: `.learnings/errors.md`\n"
        "- store actual error entries in one monthly file per month: `.learnings/errors/YYYY-MM.md`\n"
        "- inside each monthly file, group entries by day with `## YYYY-MM-DD`\n"
        "- record one compact entry per error instead of long incident writeups\n\n"
        "Actual month logs live in `.learnings/errors/`.\n",
        encoding="utf-8",
    )


def ensure_error_month_file(path: Path, month_label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(
        f"# errors — {month_label}\n\n"
        f"Compact daily error log for {month_label}.\n"
        "Keep one `## YYYY-MM-DD` section per day and one compact entry per error.\n\n",
        encoding="utf-8",
    )


def next_id(path: Path, prefix: str, day: str) -> str:
    if not path.exists():
        return f"{prefix}-{day}-001"
    text = path.read_text(encoding="utf-8")
    matches = re.findall(rf"{re.escape(prefix)}-{day}-(\d{{3}})", text)
    n = max((int(m) for m in matches), default=0) + 1
    return f"{prefix}-{day}-{n:03d}"


def build_regular_entry(args: argparse.Namespace, entry_id: str, now: dt.datetime) -> str:
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


def build_error_entry(args: argparse.Namespace, entry_id: str, now: dt.datetime) -> str:
    summary = compact(args.summary)
    tags = bullet_value(args.tags)
    related_files = bullet_value(args.related_files)
    see_also = args.see_also.strip() or "none"

    detail_problem = compact(args.error or "")
    if not detail_problem or detail_problem == summary:
        detail_problem = compact(args.context or args.details or args.error or summary)

    next_step = compact(args.action or "Investigate and document the stable fix if found.")

    detail_parts = [f"Problem: {detail_problem}."]
    if next_step:
        detail_parts.append(f"Next: {next_step}.")
    if tags != "none":
        detail_parts.append(f"Tags: {tags}.")
    if args.source.strip() and args.source.strip() != "conversation":
        detail_parts.append(f"Source: {args.source.strip()}.")
    if related_files != "none":
        detail_parts.append(f"Refs: {related_files}.")
    if see_also != "none":
        detail_parts.append(f"See: {see_also}.")

    return (
        f"- `{entry_id}` {now.strftime('%H:%M')} `{args.area}` `{args.priority}/{args.status}` — {summary}\n"
        f"  {' '.join(detail_parts)}\n"
    )


def append_regular_entry(path: Path, entry: str) -> None:
    with path.open("a", encoding="utf-8") as fh:
        if path.stat().st_size > 0:
            fh.write("\n")
        fh.write(entry)


def append_error_entry(path: Path, day: str, entry: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    headings = DAY_HEADING_RE.findall(text)
    last_heading = headings[-1] if headings else None

    if day not in headings or last_heading != day:
        if text and not text.endswith("\n"):
            text += "\n"
        if text and not text.endswith("\n\n"):
            text += "\n"
        text += f"## {day}\n\n{entry}"
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += entry

    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")

    global ROOT, LEARNINGS_DIR, STATIC_FILES, ERROR_INDEX, ERROR_DIR
    ROOT = root
    LEARNINGS_DIR = ROOT / ".learnings"
    STATIC_FILES = {
        "learning": LEARNINGS_DIR / "LEARNINGS.md",
        "feature": LEARNINGS_DIR / "FEATURE_REQUESTS.md",
    }
    ERROR_INDEX = LEARNINGS_DIR / "errors.md"
    ERROR_DIR = LEARNINGS_DIR / "errors"

    now = parse_logged_at(args.logged_at)
    day_slug = now.strftime("%Y%m%d")

    if args.type == "error":
        ensure_errors_index(ERROR_INDEX)
        month_label = now.strftime("%Y-%m")
        day_heading = now.strftime("%Y-%m-%d")
        target = ERROR_DIR / f"{month_label}.md"
        ensure_error_month_file(target, month_label)
        entry_id = next_id(target, PREFIX[args.type], day_slug)
        entry = build_error_entry(args, entry_id, now)
        append_error_entry(target, day_heading, entry)
    else:
        target = STATIC_FILES[args.type]
        ensure_regular_file(target, args.type)
        entry_id = next_id(target, PREFIX[args.type], day_slug)
        entry = build_regular_entry(args, entry_id, now)
        append_regular_entry(target, entry)

    print(f"Appended {entry_id} to {os.path.relpath(target, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

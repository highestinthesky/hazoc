#!/usr/bin/env python3
"""Record a completed learning run across daily error detail, daily summary, and .learnings artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


RUN_RE = re.compile(r"RUN-(\d{8})-(\d{3})")
LESSON_RE = re.compile(r"LRN-(\d{8})-(\d{3})")
PROTOCOL_RE = re.compile(r"PRT-(\d{8})-(\d{3})")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary", required=True, help="Succinct incident summary.")
    p.add_argument("--problem", required=True, help="Full problem details for the run.")
    p.add_argument("--lesson", action="append", default=[], help="Distilled lesson learned. Repeat for multiple lessons.")
    p.add_argument("--protocol", action="append", default=[], help="Protocol or guardrail learned/changed. Repeat for multiple items.")
    p.add_argument("--branch", default="", help="Learning branch, e.g. build-pattern or repair-pattern.")
    p.add_argument("--signal-kind", default="", help="Signal kind, e.g. request-friction.")
    p.add_argument("--context", default="")
    p.add_argument("--root-cause", default="")
    p.add_argument("--changes", default="")
    p.add_argument("--validation", default="")
    p.add_argument("--source", default="conversation")
    p.add_argument("--area", default="general")
    p.add_argument("--priority", default="medium")
    p.add_argument("--status", default="accepted")
    p.add_argument("--protocol-status", default="accepted")
    p.add_argument("--canonical-path", action="append", default=[], help="Canonical files for accepted protocol text.")
    p.add_argument("--related-file", action="append", default=[])
    p.add_argument("--logged-at", default="")
    p.add_argument("--root", default=str(Path.cwd()))
    p.add_argument("--skip-daily-summary", action="store_true")
    return p.parse_args()


def parse_logged_at(raw: str) -> dt.datetime:
    if not raw.strip():
        return dt.datetime.now().astimezone().replace(microsecond=0)
    value = raw.strip().replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.datetime.now().astimezone().tzinfo)
    return parsed.astimezone().replace(microsecond=0)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:64] or "run"


def ensure(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def next_id(path: Path, prefix: str, day_slug: str) -> str:
    pattern = {
        "RUN": RUN_RE,
        "LRN": LESSON_RE,
        "PRT": PROTOCOL_RE,
    }[prefix]
    if not path.exists():
        return f"{prefix}-{day_slug}-001"
    text = path.read_text(encoding="utf-8")
    matches = [int(n) for d, n in pattern.findall(text) if d == day_slug]
    return f"{prefix}-{day_slug}-{max(matches, default=0) + 1:03d}"


def bullet_lines(values: list[str]) -> str:
    cleaned = [v.strip() for v in values if v.strip()]
    if not cleaned:
        return "- none recorded"
    return "\n".join(f"- {v}" for v in cleaned)


def append_text(path: Path, text: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    if existing and not existing.endswith("\n\n"):
        existing += "\n"
    path.write_text(existing + text, encoding="utf-8")


def format_clock(now: dt.datetime) -> str:
    return now.strftime("%I:%M %p %Z").lstrip("0")


def main() -> int:
    args = parse_args()
    if not args.lesson and not args.protocol:
        raise SystemExit("Record at least one --lesson or --protocol so the run leaves distilled learning behind.")

    root = Path(args.root).expanduser().resolve()
    now = parse_logged_at(args.logged_at)
    day = now.strftime("%Y-%m-%d")
    day_slug = now.strftime("%Y%m%d")

    learnings_dir = root / ".learnings"
    days_dir = learnings_dir / "days" / day
    error_file = days_dir / "error.md"
    learnings_file = learnings_dir / "LEARNINGS.md"
    protocols_file = learnings_dir / "PROTOCOLS.md"
    day_file = root / "memory" / f"{day}.md"

    ensure(
        error_file,
        f"# error — {day}\n\nFull-detail learning-run log for {day}.\nKeep one section per completed learning run.\n",
    )
    ensure(
        learnings_file,
        "# Learnings\n\nRaw lessons, corrections, and best practices that are not yet promoted.\n",
    )
    ensure(
        protocols_file,
        "# Protocol Outcomes\n\nProtocol candidates, revisions, and accepted guardrails discovered through learning runs.\nAccepted protocols still need promotion into their canonical operating files and indexing in `mission-control/data/protocol.json`.\n",
    )
    day_file.parent.mkdir(parents=True, exist_ok=True)
    if not day_file.exists():
        day_file.write_text("", encoding="utf-8")

    run_id = next_id(error_file, "RUN", day_slug)
    lesson_id = next_id(learnings_file, "LRN", day_slug)
    protocol_id = next_id(protocols_file, "PRT", day_slug) if args.protocol else ""

    related_files = [p.strip() for p in args.related_file if p.strip()]
    canonical_paths = [p.strip() for p in args.canonical_path if p.strip()]

    error_entry = f"""
## [{run_id}] {slugify(args.summary)}

**Logged**: {now.isoformat()}
**Summary**: {args.summary.strip()}
**Branch**: {args.branch.strip() or 'not specified'}
**Signal Kind**: {args.signal_kind.strip() or 'not specified'}
**Area**: {args.area}
**Priority**: {args.priority}
**Status**: {args.status}
**Source**: {args.source}

### Full Problem
{args.problem.strip()}

### Context
{args.context.strip() or 'No extra context recorded.'}

### Root Cause
{args.root_cause.strip() or 'Root cause not separately recorded.'}

### Lessons Captured
{bullet_lines(args.lesson)}

### Protocol Outcomes
{bullet_lines(args.protocol)}

### Changes Made
{args.changes.strip() or 'No concrete change recorded yet.'}

### Validation
{args.validation.strip() or 'Validation not separately recorded.'}

### Related Files
{bullet_lines(related_files)}
""".lstrip()
    append_text(error_file, error_entry)

    if not args.skip_daily_summary:
        summary_bits = []
        if args.branch.strip():
            summary_bits.append(args.branch.strip())
        if args.signal_kind.strip():
            summary_bits.append(args.signal_kind.strip())
        meta = ", ".join(summary_bits)
        prefix = f"Learning run ({meta})" if meta else "Learning run"
        day_line = f"- {format_clock(now)} — {prefix}: {args.summary.strip()}.\n"
        append_text(day_file, day_line)

    learning_entry = f"""
## [{lesson_id}] {slugify(args.summary)}

**Logged**: {now.isoformat()}
**Priority**: {args.priority}
**Status**: {args.status}
**Area**: {args.area}
**Source Run**: {run_id}

### Summary
{args.summary.strip()}

### Lessons
{bullet_lines(args.lesson)}

### Promotion Notes
{('Canonical protocol paths: ' + ', '.join(canonical_paths)) if canonical_paths else 'Promote stable lessons into their canonical home when they stop feeling provisional.'}

---
""".lstrip()
    append_text(learnings_file, learning_entry)

    if args.protocol:
        protocol_entry = f"""
## [{protocol_id}] {slugify(args.summary)}

**Logged**: {now.isoformat()}
**Status**: {args.protocol_status}
**Area**: {args.area}
**Source Run**: {run_id}

### Protocol Outcomes
{bullet_lines(args.protocol)}

### Canonical Homes
{bullet_lines(canonical_paths)}

### Why
{args.root_cause.strip() or args.summary.strip()}

---
""".lstrip()
        append_text(protocols_file, protocol_entry)

    print(f"Logged {run_id}")
    print(f"- detail: {error_file.relative_to(root)}")
    print(f"- day summary: {day_file.relative_to(root)}")
    print(f"- lessons: {learnings_file.relative_to(root)}")
    if args.protocol:
        print(f"- protocols: {protocols_file.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

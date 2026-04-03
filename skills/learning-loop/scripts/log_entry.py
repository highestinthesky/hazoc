#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORKSPACE = SKILL_DIR.parent.parent
LEARNINGS_DIR = WORKSPACE / ".learnings"
ERRORS_DIR = LEARNINGS_DIR / "errors"
ERROR_INDEX_FILE = LEARNINGS_DIR / "ERROR_INDEX.md"
LEARNINGS_FILE = LEARNINGS_DIR / "LEARNINGS.md"
FEATURES_FILE = LEARNINGS_DIR / "FEATURE_REQUESTS.md"
DAYS_DIR = LEARNINGS_DIR / "days"

MONTHLY_DAY_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
ROOT_README = """# .learnings layout

This folder has four different jobs. Keep them separate.

- `LEARNINGS.md` — promoted durable lessons
- `PROTOCOLS.md` — promoted workflow/protocol changes
- `errors/` — canonical readable error history, organized by month
- `days/YYYY-MM-DD/` — day-scoped raw/archive capture only

## Reading order

If you want to understand what went wrong, read in this order:
1. `errors/YYYY-MM.md`
2. `ERROR_INDEX.md`
3. `days/YYYY-MM-DD/` only when you need date-local raw context

## Important boundary

- Do **not** treat `days/` as the main readable error ledger.
- Day folders are archive/capture surfaces.
- Canonical error history lives in `errors/`.
"""
ERRORS_README = """# Error ledger

This directory is the canonical readable error history.

- One file per month: `YYYY-MM.md`
- Read this directory before looking at `.learnings/days/`
- Day folders are archive-only context, not the primary error sink
"""
ERROR_INDEX_CONTENT = """# Error index

Canonical readable error history lives in `.learnings/errors/YYYY-MM.md`.
Use `.learnings/days/YYYY-MM-DD/` only for date-local raw/archive context.
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Append a durable learning-loop entry.")
    p.add_argument("--type", choices=["learning", "error", "feature"], required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--details", default="")
    p.add_argument("--error", default="")
    p.add_argument("--context", default="")
    p.add_argument("--action", default="")
    p.add_argument("--source", default="conversation")
    p.add_argument("--area", default="general")
    p.add_argument("--priority", default="medium")
    p.add_argument("--status", default="pending")
    p.add_argument("--tags", default="")
    p.add_argument("--related-file", action="append", default=[])
    p.add_argument("--see-also", action="append", default=[])
    p.add_argument("--json", action="store_true")
    p.add_argument("--root", default=str(WORKSPACE))
    return p.parse_args()


def ensure_file(path: Path, header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(header.rstrip() + "\n", encoding="utf-8")


def ensure_layout_files() -> None:
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    ensure_file(LEARNINGS_DIR / "README.md", ROOT_README)
    ensure_file(ERRORS_DIR / "README.md", ERRORS_README)
    ensure_file(ERROR_INDEX_FILE, ERROR_INDEX_CONTENT)


def append_text(path: Path, text: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    if existing and not existing.endswith("\n\n"):
        existing += "\n"
    path.write_text(existing + text, encoding="utf-8")


def slug_date(now: dt.datetime) -> str:
    return now.strftime("%Y%m%d")


def next_id_from_text(text: str, prefix: str, day_slug: str) -> str:
    pattern = re.compile(rf"{re.escape(prefix)}-{day_slug}-(\d{{3}})")
    matches = [int(m.group(1)) for m in pattern.finditer(text)]
    return f"{prefix}-{day_slug}-{max(matches, default=0) + 1:03d}"


def split_monthly_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    matches = list(MONTHLY_DAY_RE.finditer(text))
    if not matches:
        return text.strip(), []
    preamble = text[: matches[0].start()].strip()
    sections: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[match.end() : end].strip()
        sections.append((match.group(1), body))
    return preamble, sections


def compose_monthly(preamble: str, sections: list[tuple[str, str]]) -> str:
    chunks: list[str] = []
    if preamble.strip():
        chunks.append(preamble.strip())
    for day_key, body in sections:
        section = f"## {day_key}"
        if body.strip():
            section += f"\n\n{body.strip()}"
        chunks.append(section)
    return "\n\n".join(chunks).rstrip() + "\n"


def month_header(month_key: str) -> str:
    return (
        f"# errors — {month_key}\n\n"
        f"Canonical readable error history for {month_key}.\n"
        "Keep one `## YYYY-MM-DD` section per day.\n"
        "Use `.learnings/days/YYYY-MM-DD/` only for date-local raw/archive context."
    )


def append_to_month_day(path: Path, day_key: str, block: str, month_key: str) -> None:
    ensure_file(path, month_header(month_key))
    text = path.read_text(encoding="utf-8")
    preamble, sections = split_monthly_sections(text)
    cleaned_block = block.strip()

    for idx, (existing_day, body) in enumerate(sections):
        if existing_day != day_key:
            continue
        if cleaned_block in body:
            return
        new_body = f"{body.strip()}\n\n{cleaned_block}" if body.strip() else cleaned_block
        sections[idx] = (existing_day, new_body)
        path.write_text(compose_monthly(preamble, sections), encoding="utf-8")
        return

    sections.append((day_key, cleaned_block))
    path.write_text(compose_monthly(preamble, sections), encoding="utf-8")


def tags_list(raw: str) -> list[str]:
    return [tag.strip() for tag in raw.split(",") if tag.strip()]


def compact_error_line(entry_id: str, now: dt.datetime, area: str, priority: str, status: str, summary: str, detail: str, action: str, tags: list[str], source: str) -> str:
    summary = summary.strip().replace("\n", " ")
    detail = detail.strip().replace("\n", " ") or "No detail recorded."
    action = action.strip().replace("\n", " ") or "No next step recorded."
    tag_part = ", ".join(tags) if tags else "none"
    return (
        f"- `{entry_id}` {now.strftime('%H:%M')} `{area}` `{priority}/{status}` — {summary}\n"
        f"  Problem: {detail}. Next: {action}. Tags: {tag_part}. Source: {source}."
    )


def main() -> int:
    args = parse_args()
    now = dt.datetime.now().astimezone().replace(microsecond=0)
    day_slug = slug_date(now)
    day_key = now.strftime("%Y-%m-%d")
    month_key = now.strftime("%Y-%m")

    root = Path(args.root).expanduser().resolve()
    learnings_dir = root / ".learnings"
    errors_dir = learnings_dir / "errors"
    error_index_file = learnings_dir / "ERROR_INDEX.md"
    learnings_file = learnings_dir / "LEARNINGS.md"
    features_file = learnings_dir / "FEATURE_REQUESTS.md"

    ensure_layout_files()
    if learnings_dir != LEARNINGS_DIR:
        learnings_dir.mkdir(parents=True, exist_ok=True)
        errors_dir.mkdir(parents=True, exist_ok=True)
        ensure_file(learnings_dir / "README.md", ROOT_README)
        ensure_file(errors_dir / "README.md", ERRORS_README)
        ensure_file(error_index_file, ERROR_INDEX_CONTENT)

    target_file: Path
    entry_id: str
    body: str
    details = args.details.strip()
    error_text = args.error.strip()
    context = args.context.strip()
    action = args.action.strip()
    tags = tags_list(args.tags)
    related_files = [p.strip() for p in args.related_file if p.strip()]
    see_also = [p.strip() for p in args.see_also if p.strip()]

    if args.type == "learning":
        ensure_file(
            learnings_file,
            "# Learnings\n\nRaw lessons, corrections, and best practices that are not yet promoted.\n",
        )
        text = learnings_file.read_text(encoding="utf-8")
        entry_id = next_id_from_text(text, "LRN", day_slug)
        target_file = learnings_file
        body = f"""
## [{entry_id}] {re.sub(r'[^a-z0-9]+', '-', args.summary.strip().lower()).strip('-')[:64] or 'entry'}

**Logged**: {now.isoformat()}
**Priority**: {args.priority}
**Status**: {args.status}
**Area**: {args.area}

### Summary
{args.summary.strip()}

### Details
{details or 'No extra details recorded.'}

### Suggested Action
{action or 'No follow-up recorded.'}

### Metadata
- Source: {args.source}
- Related Files: {', '.join(related_files) if related_files else 'none'}
- Tags: {', '.join(tags) if tags else 'none'}
- See Also: {', '.join(see_also) if see_also else 'none'}

---
""".lstrip()
        append_text(target_file, body)

    elif args.type == "feature":
        ensure_file(
            features_file,
            "# Feature Requests\n\nRequests and missing capabilities to revisit later.\n",
        )
        text = features_file.read_text(encoding="utf-8")
        entry_id = next_id_from_text(text, "FEAT", day_slug)
        target_file = features_file
        body = f"""
## [{entry_id}] {re.sub(r'[^a-z0-9]+', '-', args.summary.strip().lower()).strip('-')[:64] or 'entry'}

**Logged**: {now.isoformat()}
**Priority**: {args.priority}
**Status**: {args.status}
**Area**: {args.area}

### Request
{args.summary.strip()}

### Context
{context or details or 'No extra context recorded.'}

### Suggested Next Step
{action or 'No implementation plan recorded yet.'}

### Metadata
- Source: {args.source}
- Related Files: {', '.join(related_files) if related_files else 'none'}
- Tags: {', '.join(tags) if tags else 'none'}
- See Also: {', '.join(see_also) if see_also else 'none'}

---
""".lstrip()
        append_text(target_file, body)

    else:
        monthly_file = errors_dir / f"{month_key}.md"
        existing_text = monthly_file.read_text(encoding="utf-8") if monthly_file.exists() else ""
        entry_id = next_id_from_text(existing_text, "ERR", day_slug)
        target_file = monthly_file
        body = compact_error_line(
            entry_id=entry_id,
            now=now,
            area=args.area,
            priority=args.priority,
            status=args.status,
            summary=args.summary,
            detail=error_text or details,
            action=action,
            tags=tags,
            source=args.source,
        )
        append_to_month_day(monthly_file, day_key, body, month_key)

    result: dict[str, Any] = {
        "id": entry_id,
        "type": args.type,
        "path": str(target_file.relative_to(root)),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Logged {entry_id} -> {target_file.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

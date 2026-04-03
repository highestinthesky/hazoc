#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORKSPACE = SKILL_DIR.parent.parent
LEARNINGS_DIR = WORKSPACE / ".learnings"
DAYS_DIR = LEARNINGS_DIR / "days"
ERRORS_DIR = LEARNINGS_DIR / "errors"
ERROR_INDEX_OLD = LEARNINGS_DIR / "errors.md"
ERROR_INDEX_NEW = LEARNINGS_DIR / "ERROR_INDEX.md"
MONTHLY_DAY_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
RUN_HEADING_RE = re.compile(r"^## (\[RUN-\d{8}-\d{3}\].+)$", re.MULTILINE)

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

ERROR_INDEX_HEADER = """# Error index

Canonical readable error history lives in `.learnings/errors/YYYY-MM.md`.
Use `.learnings/days/YYYY-MM-DD/` only for date-local raw/archive context.
"""

POINTER_TEMPLATE = """# Archived day error pointer

Canonical error ledger: `../../errors/{month_key}.md`

This day folder is archive-only context.
Read the monthly ledger first.
"""


def ensure(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content.rstrip() + "\n", encoding="utf-8")


def month_header(month_key: str) -> str:
    return (
        f"# errors — {month_key}\n\n"
        f"Canonical readable error history for {month_key}.\n"
        "Keep one `## YYYY-MM-DD` section per day.\n"
        "Use `.learnings/days/YYYY-MM-DD/` only for date-local raw/archive context."
    )


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


def append_to_month_day(path: Path, day_key: str, block: str) -> bool:
    month_key = path.stem
    ensure(path, month_header(month_key))
    text = path.read_text(encoding="utf-8")
    preamble, sections = split_monthly_sections(text)
    cleaned_block = block.strip()

    for idx, (existing_day, body) in enumerate(sections):
        if existing_day != day_key:
            continue
        if cleaned_block in body:
            return False
        new_body = f"{body.strip()}\n\n{cleaned_block}" if body.strip() else cleaned_block
        sections[idx] = (existing_day, new_body)
        path.write_text(compose_monthly(preamble, sections), encoding="utf-8")
        return True

    sections.append((day_key, cleaned_block))
    path.write_text(compose_monthly(preamble, sections), encoding="utf-8")
    return True


def normalize_error_index() -> None:
    monthly_files = [p.name for p in sorted(ERRORS_DIR.glob("20??-??.md"))]
    content = [ERROR_INDEX_HEADER.strip()]
    if monthly_files:
        content.append("## Monthly ledgers\n\n" + "\n".join(f"- `{name}`" for name in monthly_files))
    ERROR_INDEX_NEW.write_text("\n\n".join(content).strip() + "\n", encoding="utf-8")
    if ERROR_INDEX_OLD.exists() and ERROR_INDEX_OLD != ERROR_INDEX_NEW:
        ERROR_INDEX_OLD.unlink()


def month_key_for_day(day_key: str) -> str:
    return day_key[:7]


def clean_legacy_day_body(day_key: str, body: str) -> str:
    text = body.strip()
    if not text or "Canonical error ledger:" in text:
        return ""
    legacy_header = re.compile(
        rf"\A# error — {re.escape(day_key)}\n\n.*?(?=^## \[RUN-|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    text = legacy_header.sub("", text).strip()
    text = RUN_HEADING_RE.sub(r"### \1", text)
    return text.strip()


def normalize_day_error(day_error_file: Path) -> bool:
    day_key = day_error_file.parent.name
    month_key = month_key_for_day(day_key)
    monthly_file = ERRORS_DIR / f"{month_key}.md"
    body = day_error_file.read_text(encoding="utf-8").strip() if day_error_file.exists() else ""
    migrated = False
    cleaned = clean_legacy_day_body(day_key, body)
    if cleaned:
        migrated = append_to_month_day(monthly_file, day_key, cleaned)
    day_error_file.write_text(POINTER_TEMPLATE.format(month_key=month_key), encoding="utf-8")
    return migrated


def normalize_layout() -> dict:
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    (ERRORS_DIR / "README.md").write_text(ERRORS_README, encoding="utf-8")
    (LEARNINGS_DIR / "README.md").write_text(ROOT_README, encoding="utf-8")

    migrated_days: List[str] = []
    if DAYS_DIR.exists():
        for day_error_file in sorted(DAYS_DIR.glob("*/error.md")):
            if normalize_day_error(day_error_file):
                migrated_days.append(day_error_file.parent.name)

    normalize_error_index()
    monthly_files = [p.name for p in sorted(ERRORS_DIR.glob("20??-??.md"))]
    return {
        "migratedDays": migrated_days,
        "monthlyFiles": monthly_files,
        "errorIndex": str(ERROR_INDEX_NEW.relative_to(WORKSPACE)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize .learnings layout so canonical errors live under .learnings/errors/.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = normalize_layout()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        migrated = ", ".join(result["migratedDays"]) if result["migratedDays"] else "none"
        monthly = ", ".join(result["monthlyFiles"]) if result["monthlyFiles"] else "none"
        print(f"Migrated day errors: {migrated}")
        print(f"Monthly error files: {monthly}")
        print(f"Error index: {result['errorIndex']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORKSPACE = SKILL_DIR.parent.parent
LEARNINGS_DIR = WORKSPACE / ".learnings"
ERROR_INDEX = LEARNINGS_DIR / "ERROR_INDEX.md"
OLD_ERRORS_MD = LEARNINGS_DIR / "errors.md"
ERRORS_DIR = LEARNINGS_DIR / "errors"
DAYS_DIR = LEARNINGS_DIR / "days"
MONTHLY_DAY_RE = re.compile(r"^## \d{4}-\d{2}-\d{2}\s*$", re.MULTILINE)
LEGACY_DAILY_HEADER_RE = re.compile(r"^# error — \d{4}-\d{2}-\d{2}\s*$", re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that canonical learning errors live under .learnings/errors/ and day folders are archive pointers.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    issues = []
    if not ERROR_INDEX.exists():
        issues.append("missing .learnings/ERROR_INDEX.md")
    else:
        index_text = ERROR_INDEX.read_text(encoding="utf-8")
        if ".learnings/errors.md" in index_text:
            issues.append("ERROR_INDEX.md still references legacy .learnings/errors.md")
    if OLD_ERRORS_MD.exists():
        issues.append("legacy .learnings/errors.md still exists")
    if not ERRORS_DIR.exists():
        issues.append("missing .learnings/errors/")
    else:
        monthly_files = sorted(ERRORS_DIR.glob("20??-??.md"))
        for monthly_file in monthly_files:
            text = monthly_file.read_text(encoding="utf-8")
            if not text.startswith(f"# errors — {monthly_file.stem}"):
                issues.append(f"monthly ledger header mismatch: {monthly_file.relative_to(WORKSPACE)}")
            if not MONTHLY_DAY_RE.search(text):
                issues.append(f"monthly ledger has no day sections: {monthly_file.relative_to(WORKSPACE)}")
            if LEGACY_DAILY_HEADER_RE.search(text):
                issues.append(f"monthly ledger still embeds legacy day-file header text: {monthly_file.relative_to(WORKSPACE)}")

    for day_error_file in sorted(DAYS_DIR.glob("*/error.md")):
        text = day_error_file.read_text(encoding="utf-8")
        if "Canonical error ledger:" not in text:
            issues.append(f"day error file is not a pointer: {day_error_file.relative_to(WORKSPACE)}")
            continue
        month_key = day_error_file.parent.name[:7]
        monthly_file = ERRORS_DIR / f"{month_key}.md"
        if not monthly_file.exists():
            issues.append(f"missing monthly error ledger for {day_error_file.parent.name}: {monthly_file.relative_to(WORKSPACE)}")

    result = {"ok": not issues, "issues": issues}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["ok"]:
            print("OK")
        else:
            for issue in issues:
                print(issue)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

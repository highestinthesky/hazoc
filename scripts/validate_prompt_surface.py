#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = WORKSPACE / "mission-control" / "data" / "prompt-surface-spec.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def get_group_files(spec: dict, scope: str) -> list[str]:
    root_files = spec["groups"]["root"]["files"]
    startup_files = spec["groups"]["startup"]["files"]
    if scope == "root":
        return root_files
    if scope == "startup":
        return startup_files
    if scope == "all":
        return root_files + startup_files
    raise ValueError(f"unknown scope: {scope}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate prompt-surface budgets and rule coverage.")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC))
    parser.add_argument("--scope", choices=["root", "startup", "all"], default="all")
    args = parser.parse_args()

    spec = load_json(Path(args.spec))
    files = get_group_files(spec, args.scope)
    file_budgets = spec.get("fileBudgets", {})

    failures: list[str] = []
    total = 0
    print(f"scope={args.scope}")
    print("FILES")
    for rel in files:
        path = WORKSPACE / rel
        text = path.read_text(encoding="utf-8")
        chars = len(text)
        total += chars
        budget = file_budgets.get(rel)
        budget_note = f" / budget={budget}" if budget is not None else ""
        print(f"- {rel}: {chars}{budget_note}")
        if budget is not None and chars > int(budget):
            failures.append(f"file budget exceeded: {rel} {chars}>{budget}")

    if args.scope in ("root", "startup"):
        max_total = int(spec["groups"][args.scope]["maxCharsTotal"])
    else:
        max_total = int(spec["groups"]["all"]["maxCharsTotal"])
    print(f"TOTAL {total} / budget={max_total}")
    if total > max_total:
        failures.append(f"group budget exceeded: {total}>{max_total}")

    print("CHECKS")
    relevant = set(files)
    for check in spec.get("checks", []):
        rel = check["file"]
        if rel not in relevant:
            continue
        text = (WORKSPACE / rel).read_text(encoding="utf-8")
        missing = [needle for needle in check.get("needles", []) if needle not in text]
        if missing:
            failures.append(f"missing check {check['id']}: {missing}")
            print(f"- FAIL {check['id']}")
        else:
            print(f"- PASS {check['id']}")

    if failures:
        print("RESULT: FAIL")
        for item in failures:
            print(f"  * {item}")
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

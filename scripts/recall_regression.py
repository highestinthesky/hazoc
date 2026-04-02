#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

WORKSPACE = Path(__file__).resolve().parent.parent
CASES_PATH = WORKSPACE / "mission-control" / "data" / "recall-regression.json"
RECALL_SCRIPT = WORKSPACE / "scripts" / "recall_index.py"


def run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    cmd = [
        sys.executable,
        str(RECALL_SCRIPT),
        "search",
        "--query",
        case["query"],
        "--route",
        case.get("route", "auto"),
        "--limit",
        "3",
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=str(WORKSPACE), capture_output=True, text=True, check=True)
    result = json.loads(proc.stdout)
    errors: List[str] = []

    expected_route = case.get("expectEffectiveRoute")
    if expected_route and result.get("effectiveRoute") != expected_route:
        errors.append(f"expected effectiveRoute={expected_route}, got {result.get('effectiveRoute')}")

    expected_path = case.get("expectPathContains")
    expected_any = case.get("expectPathContainsAny") or []
    first_path = (result.get("results") or [{}])[0].get("path")
    if expected_path and expected_path not in (first_path or ""):
        errors.append(f"expected first result path to contain '{expected_path}', got '{first_path}'")
    if expected_any and not any(item in (first_path or "") for item in expected_any):
        errors.append(f"expected first result path to contain one of {expected_any}, got '{first_path}'")

    if not result.get("results"):
        errors.append("expected at least one result, got none")

    return {
        "id": case["id"],
        "ok": not errors,
        "errors": errors,
        "effectiveRoute": result.get("effectiveRoute"),
        "firstResult": (result.get("results") or [None])[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run lightweight recall regression cases.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case", action="append", default=[])
    args = parser.parse_args()

    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    if args.case:
        wanted = set(args.case)
        cases = [case for case in cases if case["id"] in wanted]

    results = [run_case(case) for case in cases]
    output = {
        "cases": results,
        "ok": all(item["ok"] for item in results),
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        for item in results:
            status = "OK" if item["ok"] else "FAIL"
            print(f"[{status}] {item['id']}")
            if item["errors"]:
                for err in item["errors"]:
                    print(f"  - {err}")
            if item["firstResult"]:
                print(f"  - first: {item['firstResult']['path']} :: {item['firstResult']['title']}")
        print(f"\nOverall: {'OK' if output['ok'] else 'FAIL'}")
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

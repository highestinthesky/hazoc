#!/usr/bin/env python3
"""Load a managed worker's durable identity + state bundle and stamp bootstrap metadata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    tmp.replace(path)


def worker_paths(root: Path, worker_id: str) -> tuple[Path, Path, Path]:
    worker_dir = root / "workers" / worker_id
    return worker_dir, worker_dir / "spec.json", worker_dir / "state.json"


def normalize_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def bootstrap(root: Path, worker_id: str, source: str, note: str) -> dict[str, Any]:
    worker_dir, spec_path, state_path = worker_paths(root, worker_id)
    if not spec_path.exists():
        raise SystemExit(f"Worker spec not found: {spec_path}")
    if not state_path.exists():
        raise SystemExit(f"Worker state not found: {state_path}")

    spec = read_json(spec_path)
    state = read_json(state_path)

    spec_worker_id = spec.get("workerId") or spec.get("id")
    state_worker_id = state.get("workerId") or state.get("id")
    if spec_worker_id != worker_id:
        raise SystemExit(f"Worker spec id mismatch: expected {worker_id}, got {spec_worker_id}")
    if state_worker_id != worker_id:
        raise SystemExit(f"Worker state id mismatch: expected {worker_id}, got {state_worker_id}")

    stamped_at = now_iso()
    state["lastBootstrapAt"] = stamped_at
    state["lastWakeAt"] = stamped_at
    state["lastWakeSource"] = source
    state["lastWakeNote"] = note
    state["bootstrapCount"] = int(state.get("bootstrapCount") or 0) + 1
    state["lastAction"] = "bootstrap"
    state["lastActionAt"] = stamped_at
    write_json(state_path, state)

    return {
        "workerId": worker_id,
        "displayName": spec.get("displayName", worker_id),
        "purpose": spec.get("purpose", ""),
        "bootstrapStamp": stamped_at,
        "paths": {
            "workerDir": normalize_rel(root, worker_dir),
            "spec": normalize_rel(root, spec_path),
            "state": normalize_rel(root, state_path),
        },
        "inputs": spec.get("inputs", {}),
        "commands": spec.get("commands", {}),
        "wakeContract": spec.get("wakeContract", {}),
        "state": state,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(WORKSPACE_ROOT))
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--source", default="manual")
    parser.add_argument("--note", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    bundle = bootstrap(root, args.worker_id.strip(), args.source.strip() or "manual", args.note.strip())
    if args.json:
        print(json.dumps(bundle, indent=2))
        return 0

    print(f"Worker: {bundle['displayName']} ({bundle['workerId']})")
    print(f"Purpose: {bundle['purpose']}")
    print(f"Bootstrap stamp: {bundle['bootstrapStamp']}")
    print("Paths:")
    for key, value in bundle["paths"].items():
        print(f"- {key}: {value}")
    if bundle["commands"]:
        print("Commands:")
        for key, value in bundle["commands"].items():
            print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

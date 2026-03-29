#!/usr/bin/env python3
"""Resolve the direct-main-task Discord completion gate before task closeout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument(
        "--decision",
        required=True,
        choices=["send", "not-applicable", "deferred"],
        help="Closeout branch to resolve before the task is considered closed.",
    )
    p.add_argument("--result", default="", help="Very short result summary for the Discord line.")
    p.add_argument("--analogy", default="", help="Tiny analogy for the Discord line.")
    p.add_argument("--reason", default="", help="Reason when the ping is not applicable or deferred.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return p.parse_args()


def load_config(root: Path) -> dict:
    path = root / "mission-control" / "data" / "notifications.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def build_send_line(config: dict, result: str, analogy: str) -> str:
    block = config["mainTaskCompletionDiscord"]
    template = block["format"]["template"]
    return template.format(very_short_result=result.strip(), tiny_analogy=analogy.strip())


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    config = load_config(root)
    block = config["mainTaskCompletionDiscord"]

    if args.decision == "send":
        if not args.result.strip() or not args.analogy.strip():
            raise SystemExit("--decision send requires both --result and --analogy")
        payload = {
            "closeoutResolved": True,
            "decision": "ping-sent",
            "channel": block["delivery"]["desiredChannel"],
            "server": block["delivery"]["desiredServer"],
            "target": block["delivery"]["to"],
            "notificationLine": build_send_line(config, args.result, args.analogy),
            "nextAction": "Send the notification line through the configured announce path before treating the task as fully closed.",
        }
    else:
        if not args.reason.strip():
            raise SystemExit(f"--decision {args.decision} requires --reason")
        payload = {
            "closeoutResolved": True,
            "decision": "not-applicable" if args.decision == "not-applicable" else "blocked-or-deferred-with-reason",
            "reason": args.reason.strip(),
            "nextAction": "Record the reason in the task closeout or daily note if it matters later.",
        }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if payload["decision"] == "ping-sent":
            print("Closeout branch: ping-sent")
            print(f"Target: {payload['server']} / {payload['channel']} ({payload['target']})")
            print(f"Notification line: {payload['notificationLine']}")
            print(payload["nextAction"])
        else:
            print(f"Closeout branch: {payload['decision']}")
            print(f"Reason: {payload['reason']}")
            print(payload["nextAction"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

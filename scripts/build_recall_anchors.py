#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from recall_anchor_lib import build_all_anchors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build compact derived anchors for task and daily-note recall.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = build_all_anchors()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"Built task anchors: {result['taskAnchors']} ({result['taskAnchorsPath']}); "
            f"daily anchors: {result['dailyAnchors']} ({result['dailyAnchorsPath']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

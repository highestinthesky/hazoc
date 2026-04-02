#!/usr/bin/env python3
"""Capture and compare OpenClaw session token usage over a time window."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

NUMERIC_FIELDS = ["totalTokens", "inputTokens", "outputTokens", "cacheRead"]


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")


def normalize_sessions(data: Any) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if isinstance(data, dict):
        # Most OpenClaw stores are { sessionKey: sessionObj }
        if all(isinstance(v, dict) for v in data.values()):
            for key, value in data.items():
                if not isinstance(value, dict):
                    continue
                row = dict(value)
                row.setdefault("sessionKey", key)
                out[str(row["sessionKey"])] = row
        elif isinstance(data.get("sessions"), list):
            for value in data["sessions"]:
                if isinstance(value, dict) and value.get("sessionKey"):
                    out[str(value["sessionKey"])] = dict(value)
    elif isinstance(data, list):
        for value in data:
            if isinstance(value, dict) and value.get("sessionKey"):
                out[str(value["sessionKey"])] = dict(value)
    return out


def parse_agent_and_route(session_key: str, fallback_agent: str | None = None) -> tuple[str, str]:
    parts = session_key.split(":")
    if len(parts) >= 3 and parts[0] == "agent":
        return parts[1], parts[2]
    return fallback_agent or "unknown", "unknown"


def label_for(row: dict[str, Any]) -> str:
    return row.get("label") or row.get("displayName") or row.get("title") or ""


def capture(state_root: Path, output: Path) -> None:
    sessions: dict[str, dict[str, Any]] = {}
    agents_root = state_root / "agents"
    for store in sorted(agents_root.glob("*/sessions/sessions.json")):
        store_agent = store.parent.parent.name
        data = load_json(store, {})
        rows = normalize_sessions(data)
        for session_key, row in rows.items():
            agent_id, route_kind = parse_agent_and_route(session_key, store_agent)
            sessions[session_key] = {
                "sessionKey": session_key,
                "storeAgent": store_agent,
                "agentId": agent_id,
                "routeKind": route_kind,
                "label": label_for(row),
                "status": row.get("status"),
                "updatedAt": row.get("updatedAt"),
                "thinkingLevel": row.get("thinkingLevel"),
                "reasoningLevel": row.get("reasoningLevel"),
                "totalTokens": int(row.get("totalTokens") or 0),
                "inputTokens": int(row.get("inputTokens") or 0),
                "outputTokens": int(row.get("outputTokens") or 0),
                "cacheRead": int(row.get("cacheRead") or 0),
            }
    payload = {
        "capturedAt": now_iso(),
        "stateRoot": str(state_root),
        "sessionCount": len(sessions),
        "sessions": sessions,
    }
    dump_json(output, payload)


def positive_delta(end_value: int, start_value: int) -> int:
    return max(0, int(end_value or 0) - int(start_value or 0))


def compare(start: dict[str, Any], end: dict[str, Any]) -> dict[str, Any]:
    start_sessions = start.get("sessions", {})
    end_sessions = end.get("sessions", {})
    keys = sorted(set(start_sessions) | set(end_sessions))

    changed_sessions: list[dict[str, Any]] = []
    totals = defaultdict(int)
    by_agent: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    by_route: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for key in keys:
        before = start_sessions.get(key, {})
        after = end_sessions.get(key, {})
        delta = {field: positive_delta(after.get(field, 0), before.get(field, 0)) for field in NUMERIC_FIELDS}
        if not any(delta.values()):
            continue
        meta = after or before
        agent_id = meta.get("agentId") or "unknown"
        route_kind = meta.get("routeKind") or "unknown"
        row = {
            "sessionKey": key,
            "label": meta.get("label") or "",
            "agentId": agent_id,
            "routeKind": route_kind,
            "startUpdatedAt": before.get("updatedAt"),
            "endUpdatedAt": after.get("updatedAt"),
            **delta,
        }
        changed_sessions.append(row)
        for field, value in delta.items():
            totals[field] += value
            by_agent[agent_id][field] += value
            by_route[route_kind][field] += value

    changed_sessions.sort(key=lambda row: (row["totalTokens"], row["inputTokens"], row["outputTokens"]), reverse=True)
    by_agent_sorted = [
        {"agentId": agent_id, **dict(metrics)}
        for agent_id, metrics in sorted(by_agent.items(), key=lambda kv: kv[1].get("totalTokens", 0), reverse=True)
    ]
    by_route_sorted = [
        {"routeKind": route_kind, **dict(metrics)}
        for route_kind, metrics in sorted(by_route.items(), key=lambda kv: kv[1].get("totalTokens", 0), reverse=True)
    ]

    return {
        "window": {
            "startCapturedAt": start.get("capturedAt"),
            "endCapturedAt": end.get("capturedAt"),
        },
        "totals": dict(totals),
        "byAgent": by_agent_sorted,
        "byRoute": by_route_sorted,
        "sessions": changed_sessions,
    }


def format_int(value: int | None) -> str:
    return f"{int(value or 0):,}"


def render_markdown(report: dict[str, Any]) -> str:
    window = report["window"]
    totals = report.get("totals", {})
    lines: list[str] = []
    lines.append("# Token Window Audit")
    lines.append("")
    lines.append(f"- Start: {window.get('startCapturedAt')}")
    lines.append(f"- End: {window.get('endCapturedAt')}")
    lines.append("")
    lines.append("## Totals")
    lines.append(f"- totalTokens delta: {format_int(totals.get('totalTokens'))}")
    lines.append(f"- inputTokens delta: {format_int(totals.get('inputTokens'))}")
    lines.append(f"- outputTokens delta: {format_int(totals.get('outputTokens'))}")
    lines.append(f"- cacheRead delta: {format_int(totals.get('cacheRead'))}")
    lines.append("")
    lines.append("Notes:")
    lines.append("- This is a session-store delta audit, not a raw provider billing export.")
    lines.append("- `cacheRead` reflects cached context reads and is not necessarily additional billed usage.")
    lines.append("")
    lines.append("## By agent")
    for row in report.get("byAgent", []):
        lines.append(
            f"- {row['agentId']}: total {format_int(row.get('totalTokens'))} | input {format_int(row.get('inputTokens'))} | output {format_int(row.get('outputTokens'))} | cacheRead {format_int(row.get('cacheRead'))}"
        )
    if not report.get("byAgent"):
        lines.append("- No token movement recorded in the window.")
    lines.append("")
    lines.append("## By route kind")
    for row in report.get("byRoute", []):
        lines.append(
            f"- {row['routeKind']}: total {format_int(row.get('totalTokens'))} | input {format_int(row.get('inputTokens'))} | output {format_int(row.get('outputTokens'))} | cacheRead {format_int(row.get('cacheRead'))}"
        )
    if not report.get("byRoute"):
        lines.append("- No token movement recorded in the window.")
    lines.append("")
    lines.append("## Sessions with token movement")
    for row in report.get("sessions", []):
        label = f" — {row['label']}" if row.get('label') else ""
        lines.append(
            f"- `{row['sessionKey']}`{label}\n"
            f"  - agent: {row['agentId']} | route: {row['routeKind']}\n"
            f"  - total {format_int(row.get('totalTokens'))} | input {format_int(row.get('inputTokens'))} | output {format_int(row.get('outputTokens'))} | cacheRead {format_int(row.get('cacheRead'))}"
        )
    if not report.get("sessions"):
        lines.append("- No session-level token movement recorded in the window.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    cap = sub.add_parser("capture")
    cap.add_argument("--state-root", required=True)
    cap.add_argument("--output", required=True)

    rep = sub.add_parser("report")
    rep.add_argument("--start", required=True)
    rep.add_argument("--end", required=True)
    rep.add_argument("--json-out", required=True)
    rep.add_argument("--md-out", required=True)

    args = parser.parse_args()
    if args.cmd == "capture":
        capture(Path(args.state_root), Path(args.output))
        return 0
    if args.cmd == "report":
        start = load_json(Path(args.start), {})
        end = load_json(Path(args.end), {})
        report = compare(start, end)
        dump_json(Path(args.json_out), report)
        md = Path(args.md_out)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(render_markdown(report), encoding="utf-8")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

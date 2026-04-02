#!/usr/bin/env python3
"""Best-effort closeout helper for main-task Discord completion updates."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_local() -> datetime:
    return datetime.now().astimezone().replace(microsecond=0)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone().replace(microsecond=0)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    temp.replace(path)


def load_config(root: Path) -> dict[str, Any]:
    path = root / "mission-control" / "data" / "notifications.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def ledger_path(root: Path) -> Path:
    return root / "mission-control" / "data" / "main-task-closeouts.json"


def load_ledger(root: Path) -> list[dict[str, Any]]:
    path = ledger_path(root)
    data = read_json(path, [])
    if not isinstance(data, list):
        raise SystemExit(f"Unexpected closeout ledger shape in {path}")
    return data


def save_ledger(root: Path, rows: list[dict[str, Any]]) -> None:
    write_json(ledger_path(root), rows)


def build_send_line(config: dict[str, Any], result: str, analogy: str) -> str:
    block = config["mainTaskCompletionDiscord"]
    template = block["format"]["template"]
    return template.format(very_short_result=result.strip(), tiny_analogy=analogy.strip())


def day_slug(dt: datetime) -> str:
    return dt.strftime("%Y%m%d")


def next_entry_id(rows: list[dict[str, Any]], dt: datetime) -> str:
    slug = day_slug(dt)
    pattern = re.compile(rf"closeout-{slug}-(\d{{3}})")
    seen = []
    for row in rows:
        match = pattern.fullmatch(str(row.get("id", "")))
        if match:
            seen.append(int(match.group(1)))
    return f"closeout-{slug}-{max(seen, default=0) + 1:03d}"


def save_entry(root: Path, entry: dict[str, Any]) -> None:
    rows = load_ledger(root)
    rows.append(entry)
    save_ledger(root, rows)


def update_entry(root: Path, entry_id: str, mutate) -> dict[str, Any]:
    rows = load_ledger(root)
    updated: dict[str, Any] | None = None
    for row in rows:
        if row.get("id") == entry_id:
            mutate(row)
            updated = row
            break
    if updated is None:
        raise SystemExit(f"Unknown closeout id: {entry_id}")
    save_ledger(root, rows)
    return updated


def closeout_prompt(line: str) -> str:
    return (
        "Reply with EXACTLY the following one-line text and nothing else:\n"
        f"{line}\n"
        "No preface. No markdown fences. No extra text."
    )


def enqueue_best_effort_send(
    root: Path,
    result: str,
    analogy: str,
    task_ref: str,
    note: str,
    source_session: str,
    created_at_raw: str | None,
    as_json: bool,
    dry_run: bool,
) -> int:
    config = load_config(root)
    block = config["mainTaskCompletionDiscord"]
    rows = load_ledger(root)
    created_at = parse_dt(created_at_raw) or now_local()
    entry_id = next_entry_id(rows, created_at)
    line = build_send_line(config, result, analogy)
    entry = {
        "id": entry_id,
        "createdAt": created_at.isoformat(),
        "status": "preview" if dry_run else "send-requested",
        "result": result.strip(),
        "analogy": analogy.strip(),
        "notificationLine": line,
        "taskRef": task_ref.strip(),
        "note": note.strip(),
        "sourceSession": source_session.strip(),
        "delivery": {
            "mode": block["delivery"]["mode"],
            "channel": block["delivery"]["channel"],
            "to": block["delivery"]["to"],
            "desiredServer": block["delivery"]["desiredServer"],
            "desiredChannel": block["delivery"]["desiredChannel"],
            "fallbackTo": block["delivery"].get("fallbackTo"),
            "fallbackChannelLabel": block["delivery"].get("fallbackChannelLabel"),
            "fallbackPolicy": block["delivery"].get("fallbackPolicy", "manual-only"),
            "bestEffort": block["delivery"].get("bestEffort", True),
        },
        "policy": {
            "bestEffort": True,
            "blocksTaskClosure": False,
            "missedPingTolerance": "acceptable",
        },
        "cronJobId": None,
        "enqueueResponse": None,
        "error": None,
    }
    save_entry(root, entry)

    payload = {
        "closeoutResolved": True,
        "taskMayClose": True,
        "decision": "best-effort-send-preview" if dry_run else "best-effort-send-requested",
        "id": entry_id,
        "notificationLine": line,
        "target": block["delivery"]["to"],
        "server": block["delivery"]["desiredServer"],
        "channel": block["delivery"]["desiredChannel"],
        "ledgerFile": str(ledger_path(root)),
    }

    if dry_run:
        if as_json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Preview closeout: {entry_id}")
            print(f"Target: {payload['server']} / {payload['channel']} ({payload['target']})")
            print(f"Notification line: {payload['notificationLine']}")
        return 0

    cmd = [
        "openclaw",
        "cron",
        "add",
        "--json",
        "--name",
        f"main-task-closeout-{entry_id}",
        "--at",
        "+5s",
        "--session",
        "isolated",
        "--message",
        closeout_prompt(line),
        "--light-context",
        "--thinking",
        "minimal",
        "--announce",
        "--channel",
        block["delivery"]["channel"],
        "--to",
        block["delivery"]["to"],
        "--best-effort-deliver",
        "--delete-after-run",
        "--wake",
        "now",
        "--timeout-seconds",
        "20",
    ]

    proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    raw = stdout or stderr

    if proc.returncode == 0:
        parsed: dict[str, Any] | None = None
        if stdout:
            try:
                obj = json.loads(stdout)
                if isinstance(obj, dict):
                    parsed = obj
            except json.JSONDecodeError:
                parsed = None

        def mutate(row: dict[str, Any]) -> None:
            row["status"] = "send-enqueued"
            row["enqueueRequestedAt"] = now_local().isoformat()
            row["enqueueResponse"] = parsed if parsed is not None else raw
            row["cronJobId"] = (
                (parsed or {}).get("id")
                or (parsed or {}).get("jobId")
                or (parsed or {}).get("job", {}).get("id")
            )

        updated = update_entry(root, entry_id, mutate)
        payload.update(
            {
                "decision": "best-effort-send-requested",
                "cronJobId": updated.get("cronJobId"),
                "enqueueResponse": updated.get("enqueueResponse"),
            }
        )
        if as_json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Closeout send requested: {entry_id}")
            print(f"Target: {payload['server']} / {payload['channel']} ({payload['target']})")
            print(f"Notification line: {payload['notificationLine']}")
        return 0

    def mutate_error(row: dict[str, Any]) -> None:
        row["status"] = "send-enqueue-failed"
        row["enqueueRequestedAt"] = now_local().isoformat()
        row["error"] = raw or f"openclaw cron add exited {proc.returncode}"

    update_entry(root, entry_id, mutate_error)
    payload.update(
        {
            "decision": "best-effort-send-failed",
            "error": raw or f"openclaw cron add exited {proc.returncode}",
        }
    )
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Closeout send failed: {entry_id}")
        print(payload["error"])
    return 1


def resolve_without_send(root: Path, decision: str, reason: str, task_ref: str, source_session: str, as_json: bool) -> int:
    rows = load_ledger(root)
    created_at = now_local()
    entry_id = next_entry_id(rows, created_at)
    status = "not-applicable" if decision == "not-applicable" else "blocked-deferred"
    entry = {
        "id": entry_id,
        "createdAt": created_at.isoformat(),
        "status": status,
        "reason": reason.strip(),
        "taskRef": task_ref.strip(),
        "sourceSession": source_session.strip(),
        "policy": {
            "bestEffort": True,
            "blocksTaskClosure": False,
            "missedPingTolerance": "acceptable",
        },
    }
    save_entry(root, entry)
    payload = {
        "closeoutResolved": True,
        "taskMayClose": True,
        "decision": status,
        "id": entry_id,
        "reason": reason.strip(),
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Closeout branch: {status}")
        print(f"Reason: {reason.strip()}")
    return 0


def list_pending(root: Path, as_json: bool) -> int:
    rows = load_ledger(root)
    pending = [row for row in rows if row.get("status") in {"send-requested", "send-enqueued"}]
    if as_json:
        print(json.dumps(pending, indent=2))
    else:
        for row in pending:
            print(f"{row.get('id')}\t{row.get('status')}\t{row.get('createdAt')}\t{row.get('result','')}")
    return 0


def dispatch_noop(as_json: bool) -> int:
    payload = {"shouldSend": False, "message": "NO_REPLY", "note": "Closeout recovery worker retired; no dispatch loop remains."}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("NO_REPLY")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument("--json", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="Build/log the closeout payload without enqueueing a cron send.")
    p.add_argument("--decision", choices=["send", "not-applicable", "deferred"], help="Compatibility mode from the earlier helper.")
    p.add_argument("--result", default="", help="Very short result summary for the Discord line.")
    p.add_argument("--analogy", default="", help="Tiny analogy for the Discord line.")
    p.add_argument("--reason", default="", help="Reason when the ping is not applicable or deferred.")
    p.add_argument("--task-ref", default="", help="Optional task or request reference.")
    p.add_argument("--note", default="", help="Optional operator note.")
    p.add_argument("--source-session", default="", help="Optional source session key.")
    p.add_argument("--created-at", default="", help="Optional ISO timestamp override.")
    p.add_argument("--timeout-ms", type=int, default=30000, help="Unused compatibility field from the earlier helper.")
    p.add_argument("--expect-final", action="store_true", help="Unused compatibility flag from the earlier helper.")

    sub = p.add_subparsers(dest="action")

    send_parser = sub.add_parser("send-now")
    send_parser.add_argument("--result", required=True)
    send_parser.add_argument("--analogy", required=True)
    send_parser.add_argument("--task-ref", default="")
    send_parser.add_argument("--note", default="")
    send_parser.add_argument("--source-session", default="")
    send_parser.add_argument("--created-at", default="")
    send_parser.add_argument("--dry-run", action="store_true")

    queue_send_parser = sub.add_parser("queue-send")
    queue_send_parser.add_argument("--result", required=True)
    queue_send_parser.add_argument("--analogy", required=True)
    queue_send_parser.add_argument("--task-ref", default="")
    queue_send_parser.add_argument("--note", default="")
    queue_send_parser.add_argument("--source-session", default="")
    queue_send_parser.add_argument("--created-at", default="")
    queue_send_parser.add_argument("--dry-run", action="store_true")

    queue_and_wake_parser = sub.add_parser("queue-and-wake")
    queue_and_wake_parser.add_argument("--result", required=True)
    queue_and_wake_parser.add_argument("--analogy", required=True)
    queue_and_wake_parser.add_argument("--task-ref", default="")
    queue_and_wake_parser.add_argument("--note", default="")
    queue_and_wake_parser.add_argument("--source-session", default="")
    queue_and_wake_parser.add_argument("--created-at", default="")
    queue_and_wake_parser.add_argument("--dry-run", action="store_true")

    dispatch_one_parser = sub.add_parser("dispatch-one")
    dispatch_one_parser.add_argument("--id", required=True)

    sub.add_parser("dispatch-next")
    sub.add_parser("list-pending")

    not_app_parser = sub.add_parser("resolve-not-applicable")
    not_app_parser.add_argument("--reason", required=True)
    not_app_parser.add_argument("--task-ref", default="")
    not_app_parser.add_argument("--source-session", default="")

    deferred_parser = sub.add_parser("resolve-deferred")
    deferred_parser.add_argument("--reason", required=True)
    deferred_parser.add_argument("--task-ref", default="")
    deferred_parser.add_argument("--source-session", default="")

    return p.parse_args(argv)


def compatibility_mode(args: argparse.Namespace, root: Path) -> int:
    if args.decision == "send":
        if not args.result.strip() or not args.analogy.strip():
            raise SystemExit("--decision send requires both --result and --analogy")
        return enqueue_best_effort_send(root, args.result, args.analogy, args.task_ref, args.note, args.source_session, args.created_at, args.json, args.dry_run)
    if args.decision == "not-applicable":
        return resolve_without_send(root, "not-applicable", args.reason, args.task_ref, args.source_session, args.json)
    if args.decision == "deferred":
        return resolve_without_send(root, "deferred", args.reason, args.task_ref, args.source_session, args.json)
    raise SystemExit("No action specified")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).expanduser().resolve()

    if args.action in {"send-now", "queue-send", "queue-and-wake"}:
        return enqueue_best_effort_send(root, args.result, args.analogy, args.task_ref, args.note, args.source_session, args.created_at, args.json, args.dry_run)
    if args.action == "dispatch-one":
        return dispatch_noop(args.json)
    if args.action == "dispatch-next":
        return dispatch_noop(args.json)
    if args.action == "list-pending":
        return list_pending(root, args.json)
    if args.action == "resolve-not-applicable":
        return resolve_without_send(root, "not-applicable", args.reason, args.task_ref, args.source_session, args.json)
    if args.action == "resolve-deferred":
        return resolve_without_send(root, "deferred", args.reason, args.task_ref, args.source_session, args.json)
    if args.decision:
        return compatibility_mode(args, root)
    raise SystemExit("No action specified")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

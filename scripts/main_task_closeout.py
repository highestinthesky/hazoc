#!/usr/bin/env python3
"""Durable closeout helper for main-task Discord completion updates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

STALE_SENDING_MINUTES = 10


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


def queue_path(root: Path) -> Path:
    return root / "mission-control" / "data" / "main-task-closeouts.json"


def load_queue(root: Path) -> list[dict[str, Any]]:
    path = queue_path(root)
    data = read_json(path, [])
    if not isinstance(data, list):
        raise SystemExit(f"Unexpected closeout queue shape in {path}")
    return data


def save_queue(root: Path, rows: list[dict[str, Any]]) -> None:
    write_json(queue_path(root), rows)


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


def queue_send(root: Path, result: str, analogy: str, task_ref: str, note: str, source_session: str, created_at_raw: str | None, as_json: bool) -> int:
    config = load_config(root)
    block = config["mainTaskCompletionDiscord"]
    rows = load_queue(root)
    created_at = parse_dt(created_at_raw) or now_local()
    entry_id = next_entry_id(rows, created_at)
    line = build_send_line(config, result, analogy)
    entry = {
        "id": entry_id,
        "createdAt": created_at.isoformat(),
        "status": "queued",
        "result": result.strip(),
        "analogy": analogy.strip(),
        "notificationLine": line,
        "taskRef": task_ref.strip(),
        "note": note.strip(),
        "sourceSession": source_session.strip(),
        "delivery": {
            "channel": block["delivery"]["channel"],
            "to": block["delivery"]["to"],
            "desiredServer": block["delivery"]["desiredServer"],
            "desiredChannel": block["delivery"]["desiredChannel"],
            "fallbackTo": block["delivery"].get("fallbackTo"),
            "fallbackChannelLabel": block["delivery"].get("fallbackChannelLabel"),
        },
        "resolution": "ping-sent",
        "attempts": 0,
        "dispatchStartedAt": None,
        "dispatchedAt": None,
        "dispatchJobId": None,
        "recoveryJob": block.get("closeoutGate", {}).get("recoveryJobName", "recover-main-task-closeouts"),
        "recoveryWorkerId": block.get("closeoutGate", {}).get("workerId", "recover-main-task-closeouts"),
        "recoveryWorkerSpec": block.get("closeoutGate", {}).get("workerSpec", "workers/recover-main-task-closeouts/spec.json"),
        "recoveryWorkerState": block.get("closeoutGate", {}).get("workerState", "workers/recover-main-task-closeouts/state.json"),
    }
    rows.append(entry)
    save_queue(root, rows)
    payload = {
        "closeoutResolved": False,
        "decision": "queued-for-dispatch",
        "id": entry_id,
        "notificationLine": line,
        "target": block["delivery"]["to"],
        "server": block["delivery"]["desiredServer"],
        "channel": block["delivery"]["desiredChannel"],
        "queueFile": str(queue_path(root)),
        "nextAction": "Create an immediate isolated cron announce job that dispatches this queued closeout, then treat the task as closed only after the job is queued.",
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Queued closeout: {entry_id}")
        print(f"Target: {payload['server']} / {payload['channel']} ({payload['target']})")
        print(f"Notification line: {payload['notificationLine']}")
        print(payload["nextAction"])
    return 0


def mark_job(root: Path, entry_id: str, job_id: str, as_json: bool) -> int:
    rows = load_queue(root)
    for row in rows:
        if row.get("id") == entry_id:
            row["dispatchJobId"] = job_id.strip()
            if row.get("status") == "queued":
                row["status"] = "armed"
            row["scheduledAt"] = now_local().isoformat()
            save_queue(root, rows)
            payload = {"ok": True, "id": entry_id, "jobId": job_id.strip(), "status": row["status"]}
            if as_json:
                print(json.dumps(payload, indent=2))
            else:
                print(f"Marked {entry_id} with dispatch job {job_id.strip()}")
            return 0
    raise SystemExit(f"Unknown closeout id: {entry_id}")


def stale_sending(row: dict[str, Any], now: datetime) -> bool:
    if row.get("status") != "sending":
        return False
    started = parse_dt(row.get("dispatchStartedAt"))
    if not started:
        return True
    return now - started >= timedelta(minutes=STALE_SENDING_MINUTES)


def claim_entry(rows: list[dict[str, Any]], target_id: str | None) -> dict[str, Any] | None:
    now = now_local()
    candidates = []
    for row in rows:
        status = row.get("status")
        if status in {"queued", "armed"} or stale_sending(row, now):
            if target_id is None or row.get("id") == target_id:
                candidates.append(row)
    if not candidates:
        return None
    candidates.sort(key=lambda row: row.get("createdAt", ""))
    chosen = candidates[0]
    chosen["status"] = "sending"
    chosen["attempts"] = int(chosen.get("attempts") or 0) + 1
    chosen["dispatchStartedAt"] = now.isoformat()
    chosen["lastAttemptAt"] = now.isoformat()
    return chosen


def dispatch(root: Path, entry_id: str | None, as_json: bool, record_only: bool = False) -> int:
    rows = load_queue(root)
    row = claim_entry(rows, entry_id)
    if row is None:
        if as_json:
            print(json.dumps({"shouldSend": False, "message": "NO_REPLY"}, indent=2))
        else:
            print("NO_REPLY")
        return 0

    now = now_local()
    row["status"] = "dispatched" if record_only else "dispatched"
    row["dispatchedAt"] = now.isoformat()
    save_queue(root, rows)
    if as_json:
        print(json.dumps({
            "shouldSend": True,
            "id": row["id"],
            "notificationLine": row["notificationLine"],
            "status": row["status"],
        }, indent=2))
    else:
        print(row["notificationLine"])
    return 0


def resolve_without_send(root: Path, decision: str, reason: str, task_ref: str, source_session: str, as_json: bool) -> int:
    rows = load_queue(root)
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
        "resolution": status,
    }
    rows.append(entry)
    save_queue(root, rows)
    payload = {"closeoutResolved": True, "decision": status, "id": entry_id, "reason": reason.strip()}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Closeout branch: {status}")
        print(f"Reason: {reason.strip()}")
    return 0


def list_pending(root: Path, as_json: bool) -> int:
    rows = load_queue(root)
    pending = [row for row in rows if row.get("status") in {"queued", "armed", "sending"}]
    if as_json:
        print(json.dumps(pending, indent=2))
    else:
        for row in pending:
            print(f"{row.get('id')}\t{row.get('status')}\t{row.get('createdAt')}\t{row.get('result','')}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument("--json", action="store_true")
    p.add_argument("--decision", choices=["send", "not-applicable", "deferred"], help="Compatibility mode from the earlier helper.")
    p.add_argument("--result", default="", help="Very short result summary for the Discord line.")
    p.add_argument("--analogy", default="", help="Tiny analogy for the Discord line.")
    p.add_argument("--reason", default="", help="Reason when the ping is not applicable or deferred.")
    p.add_argument("--task-ref", default="", help="Optional task or request reference.")
    p.add_argument("--note", default="", help="Optional operator note.")
    p.add_argument("--source-session", default="", help="Optional source session key.")
    p.add_argument("--created-at", default="", help="Optional ISO timestamp override.")

    sub = p.add_subparsers(dest="action")

    queue_send_parser = sub.add_parser("queue-send")
    queue_send_parser.add_argument("--result", required=True)
    queue_send_parser.add_argument("--analogy", required=True)
    queue_send_parser.add_argument("--task-ref", default="")
    queue_send_parser.add_argument("--note", default="")
    queue_send_parser.add_argument("--source-session", default="")
    queue_send_parser.add_argument("--created-at", default="")

    mark_job_parser = sub.add_parser("mark-job")
    mark_job_parser.add_argument("--id", required=True)
    mark_job_parser.add_argument("--job-id", required=True)

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
        config = load_config(root)
        block = config["mainTaskCompletionDiscord"]
        payload = {
            "closeoutResolved": False,
            "decision": "queued-for-dispatch",
            "notificationLine": build_send_line(config, args.result, args.analogy),
            "target": block["delivery"]["to"],
            "server": block["delivery"]["desiredServer"],
            "channel": block["delivery"]["desiredChannel"],
            "nextAction": "Use queue-send for durable dispatch before task closure.",
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(payload["notificationLine"])
        return 0
    if args.decision == "not-applicable":
        return resolve_without_send(root, "not-applicable", args.reason, args.task_ref, args.source_session, args.json)
    if args.decision == "deferred":
        return resolve_without_send(root, "deferred", args.reason, args.task_ref, args.source_session, args.json)
    raise SystemExit("No action specified")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).expanduser().resolve()

    if args.action == "queue-send":
        return queue_send(root, args.result, args.analogy, args.task_ref, args.note, args.source_session, args.created_at, args.json)
    if args.action == "mark-job":
        return mark_job(root, getattr(args, 'id'), getattr(args, 'job_id'), args.json)
    if args.action == "dispatch-one":
        return dispatch(root, getattr(args, 'id'), args.json)
    if args.action == "dispatch-next":
        return dispatch(root, None, args.json)
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

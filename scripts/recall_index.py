#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from recall_anchor_lib import build_all_anchors

WORKSPACE = Path(__file__).resolve().parent.parent
INDEX_DIR = WORKSPACE / "tmp" / "recall-index"
CHUNKS_PATH = INDEX_DIR / "chunks.json"
STATE_PATH = INDEX_DIR / "state.json"
CONFIG_PATH = WORKSPACE / "mission-control" / "data" / "recall-sources.json"
TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")
DATE_FILE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.md$")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")

ROUTE_STAGES: Dict[str, List[List[str]]] = {
    "preference": [["preference", "curated"], ["protocol"], ["reference"]],
    "active": [["active"], ["task", "daily"], ["curated"]],
    "task": [["task"], ["active"], ["daily", "curated"]],
    "recent": [["active", "daily"], ["task"], ["curated"]],
    "history": [["curated", "protocol", "daily"], ["task", "reference"]],
    "protocol": [["protocol"], ["reference"], ["curated"]],
    "branch": [["branch"], ["task", "reference"]],
    "unknown": [["active", "preference", "curated", "task"], ["daily", "protocol"], ["reference", "branch"]],
}

ROUTE_HINTS = {
    "preference": ["prefer", "preference", "call them", "tone", "identity", "who am i", "persona"],
    "active": ["current", "currently", "now", "next step", "blocker", "handoff", "active", "focus", "what were we doing", "what were we working on", "where were we"],
    "task": ["task", "project", "workbench", "on hold", "archived", "lane", "task-"],
    "recent": ["today", "yesterday", "this morning", "this afternoon", "recent", "earlier today", "just now"],
    "history": ["when did", "last week", "last month", "history", "previous", "previously", "decide", "decision", "date"],
    "protocol": ["protocol", "rule", "workflow", "process", "playbook", "should i", "how do we handle"],
    "branch": ["discord", "telegram", "branch", "agent", "worker", "guest-safe-web", "discord-control", "channel"],
}

GENERIC_REANCHOR_PHRASES = {
    "what were we doing",
    "what were we working on",
    "where were we",
    "what is the current focus",
    "what's the current focus",
}


def default_source_rules() -> List[Dict[str, str]]:
    return [
        {"pattern": "SOUL.md", "kind": "identity", "route": "preference"},
        {"pattern": "IDENTITY.md", "kind": "identity", "route": "preference"},
        {"pattern": "USER.md", "kind": "user", "route": "preference"},
        {"pattern": "MEMORY.md", "kind": "curated", "route": "curated"},
        {"pattern": "AGENTS.md", "kind": "protocol", "route": "protocol"},
        {"pattern": "TOOLS.md", "kind": "reference", "route": "reference"},
        {"pattern": "PROTOCOL_SPINE.md", "kind": "protocol_spine", "route": "protocol"},
        {"pattern": "RECALL_MAP.md", "kind": "recall_map", "route": "protocol"},
        {"pattern": "memory/active-state.md", "kind": "active", "route": "active"},
        {"pattern": "tmp/recall-anchors/task-anchors.json", "kind": "task_anchor_json", "route": "task"},
        {"pattern": "mission-control/data/tasks.json", "kind": "task_json", "route": "task"},
        {"pattern": "tmp/recall-anchors/daily-anchors.json", "kind": "daily_anchor_json", "route": "daily"},
        {"pattern": "mission-control/data/protocol.json", "kind": "protocol_json", "route": "protocol"},
        {"pattern": "memory/20??-??-??.md", "kind": "daily", "route": "daily"},
        {"pattern": "references/**/*.md", "kind": "reference", "route": "reference"},
        {"pattern": "agent-namecards/**/*.md", "kind": "branch_doc", "route": "branch"},
        {"pattern": "agent-namecards/**/*.json", "kind": "branch_json", "route": "branch"},
        {"pattern": "workers/**/*.json", "kind": "worker_json", "route": "branch"},
        {"pattern": "skills/**/SKILL.md", "kind": "skill", "route": "protocol"},
        {"pattern": "skills/**/references/**/*.md", "kind": "skill_reference", "route": "reference"},
    ]


def load_source_rules() -> List[Dict[str, str]]:
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        rules = data.get("rules")
        if isinstance(rules, list) and rules:
            return rules
    return default_source_rules()


def source_config_digest() -> str:
    payload = json.dumps(load_source_rules(), sort_keys=True)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def relpath(path: Path) -> str:
    return str(path.resolve().relative_to(WORKSPACE.resolve()))


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


def short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def iter_source_specs() -> Iterable[Dict[str, Any]]:
    seen: set[Path] = set()

    def add(path: Path, kind: str, route: str) -> Optional[Dict[str, Any]]:
        path = path.resolve()
        if not path.exists() or not path.is_file() or path in seen:
            return None
        seen.add(path)
        return {"path": path, "kind": kind, "route": route}

    for rule in load_source_rules():
        pattern = rule["pattern"]
        kind = rule["kind"]
        route = rule["route"]
        matched = sorted(WORKSPACE.glob(pattern))
        for path in matched:
            spec = add(path, kind, route)
            if spec:
                yield spec


def manifest_for_sources(sources: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    manifest = []
    for spec in sources:
        stat = spec["path"].stat()
        manifest.append(
            {
                "path": relpath(spec["path"]),
                "kind": spec["kind"],
                "route": spec["route"],
                "size": stat.st_size,
                "mtime": round(stat.st_mtime, 6),
            }
        )
    manifest.sort(key=lambda item: item["path"])
    return manifest


def load_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text())


def ensure_derived_sources() -> Dict[str, Any]:
    return build_all_anchors()


def index_stale() -> bool:
    ensure_derived_sources()
    sources = list(iter_source_specs())
    state = load_state()
    saved_manifest = state.get("manifest")
    current_manifest = manifest_for_sources(sources)
    return (
        saved_manifest != current_manifest
        or state.get("configDigest") != source_config_digest()
        or not CHUNKS_PATH.exists()
    )


def flatten_json(value: Any, prefix: str = "") -> List[str]:
    lines: List[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            lines.extend(flatten_json(child, child_prefix))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            child_prefix = f"{prefix}[{idx}]" if prefix else f"[{idx}]"
            lines.extend(flatten_json(child, child_prefix))
    else:
        lines.append(f"{prefix}: {value}")
    return lines


def chunk_text_file(path: Path, kind: str, route: str) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    lines = text.splitlines()
    max_chars = 700 if kind in {"daily", "active"} else 950 if route == "protocol" else 1200
    heading_title = path.name
    start_line: Optional[int] = None
    buffer: List[str] = []
    chunks: List[Dict[str, Any]] = []

    def emit(end_line: int) -> None:
        nonlocal buffer, start_line
        content = "\n".join(buffer).strip()
        if not content or start_line is None:
            buffer = []
            start_line = None
            return
        chunk_id = short_hash(f"{relpath(path)}::{kind}::{start_line}:{end_line}::{heading_title}")
        chunks.append(
            {
                "id": chunk_id,
                "path": relpath(path),
                "kind": kind,
                "route": route,
                "title": heading_title,
                "source_ref": relpath(path),
                "start_line": start_line,
                "end_line": end_line,
                "updated_at": None,
                "content": content,
            }
        )
        buffer = []
        start_line = None

    current_len = 0
    for line_no, line in enumerate(lines, start=1):
        heading_match = HEADING_RE.match(line)
        if heading_match:
            if buffer:
                emit(line_no - 1)
            heading_text = heading_match.group(1).strip()
            heading_title = f"{path.name} — {heading_text}"
            buffer = [line]
            start_line = line_no
            current_len = len(line)
            continue

        if buffer and current_len >= max_chars and (not line.strip() or LIST_RE.match(line)):
            emit(line_no - 1)
            buffer = []
            start_line = None
            current_len = 0

        if start_line is None:
            start_line = line_no
        buffer.append(line)
        current_len += len(line) + 1

    if buffer:
        emit(len(lines))

    return chunks


def chunk_tasks_json(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks: List[Dict[str, Any]] = []
    for task in data:
        task_id = task.get("id", "unknown-task")
        title = task.get("title", task_id)
        content = "\n".join(
            [
                f"Task ID: {task_id}",
                f"Title: {title}",
                f"Lane: {task.get('lane', '')}",
                f"Notes: {task.get('notes', '')}",
                f"Description: {task.get('description', '')}",
                f"Scheduled start: {task.get('scheduledStart', '')}",
                f"Scheduled end: {task.get('scheduledEnd', '')}",
            ]
        ).strip()
        chunks.append(
            {
                "id": short_hash(f"task::{task_id}"),
                "path": relpath(path),
                "kind": "task",
                "route": "task",
                "title": title,
                "source_ref": task_id,
                "start_line": None,
                "end_line": None,
                "updated_at": task.get("updatedAt") or task.get("createdAt"),
                "content": content,
            }
        )
    return chunks


def chunk_protocol_json(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks: List[Dict[str, Any]] = []
    for item in data:
        protocol_id = item.get("id", "unknown-protocol")
        title = item.get("title", protocol_id)
        content = "\n".join(
            [
                f"Protocol ID: {protocol_id}",
                f"Title: {title}",
                f"Category: {item.get('category', '')}",
                f"Cadence: {item.get('cadence', '')}",
                f"Scope: {item.get('scope', '')}",
                f"Summary: {item.get('summary', '')}",
                f"Canonical paths: {', '.join(item.get('canonicalPaths', []))}",
            ]
        ).strip()
        chunks.append(
            {
                "id": short_hash(f"protocol::{protocol_id}"),
                "path": relpath(path),
                "kind": "protocol_entry",
                "route": "protocol",
                "title": title,
                "source_ref": protocol_id,
                "start_line": None,
                "end_line": None,
                "updated_at": item.get("updatedAt") or item.get("createdAt"),
                "content": content,
            }
        )
    return chunks


def chunk_task_anchors_json(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks: List[Dict[str, Any]] = []
    for item in data:
        task_id = item.get("id", "unknown-task")
        title = item.get("title", task_id)
        highlights = item.get("highlights", [])
        content = "\n".join(
            [
                f"Task ID: {task_id}",
                f"Title: {title}",
                f"Lane: {item.get('lane', '')}",
                f"Summary: {item.get('summary', '')}",
                f"Highlights: {' | '.join(highlights)}",
                f"Keywords: {' | '.join(item.get('keywords', []))}",
            ]
        ).strip()
        chunks.append(
            {
                "id": short_hash(f"task-anchor::{task_id}"),
                "path": relpath(path),
                "kind": "task_anchor",
                "route": "task",
                "title": title,
                "source_ref": task_id,
                "start_line": None,
                "end_line": None,
                "updated_at": item.get("updatedAt"),
                "content": content,
            }
        )
    return chunks


def chunk_daily_anchors_json(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks: List[Dict[str, Any]] = []
    for item in data:
        daily_ref = item.get("date", "unknown-date")
        title = f"Daily anchor {daily_ref}"
        content = "\n".join(
            [
                f"Date: {daily_ref}",
                f"Source path: {item.get('path', '')}",
                f"Summary: {item.get('summary', '')}",
                f"Headings: {' | '.join(item.get('headings', []))}",
                f"Recent bullets: {' | '.join(item.get('recentBullets', []))}",
                f"Bullet count: {item.get('bulletCount', 0)}",
            ]
        ).strip()
        chunks.append(
            {
                "id": short_hash(f"daily-anchor::{daily_ref}"),
                "path": relpath(path),
                "kind": "daily_anchor",
                "route": "daily",
                "title": title,
                "source_ref": daily_ref,
                "start_line": None,
                "end_line": None,
                "updated_at": f"{daily_ref}T23:59:59+00:00",
                "content": content,
            }
        )
    return chunks


def chunk_generic_json(path: Path, kind: str, route: str) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    content = "\n".join(flatten_json(data))
    if not content.strip():
        return []
    return [
        {
            "id": short_hash(f"{relpath(path)}::{kind}"),
            "path": relpath(path),
            "kind": kind,
            "route": route,
            "title": path.stem,
            "source_ref": relpath(path),
            "start_line": None,
            "end_line": None,
            "updated_at": None,
            "content": content,
        }
    ]


def build_index() -> Dict[str, Any]:
    anchor_state = ensure_derived_sources()
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    sources = list(iter_source_specs())
    chunks: List[Dict[str, Any]] = []
    for spec in sources:
        path = spec["path"]
        kind = spec["kind"]
        route = spec["route"]
        if path.suffix.lower() == ".json":
            if path.name == "tasks.json":
                chunks.extend(chunk_tasks_json(path))
            elif path.name == "task-anchors.json":
                chunks.extend(chunk_task_anchors_json(path))
            elif path.name == "daily-anchors.json":
                chunks.extend(chunk_daily_anchors_json(path))
            elif path.name == "protocol.json":
                chunks.extend(chunk_protocol_json(path))
            else:
                chunks.extend(chunk_generic_json(path, kind, route))
        else:
            chunks.extend(chunk_text_file(path, kind, route))
    CHUNKS_PATH.write_text(json.dumps(chunks, indent=2) + "\n", encoding="utf-8")
    state = {
        "builtAt": now_iso(),
        "chunkCount": len(chunks),
        "sourceCount": len(sources),
        "anchorState": anchor_state,
        "configPath": relpath(CONFIG_PATH) if CONFIG_PATH.exists() else None,
        "configDigest": source_config_digest(),
        "manifest": manifest_for_sources(sources),
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state


def ensure_index() -> Dict[str, Any]:
    if index_stale():
        return build_index()
    return load_state()


def load_chunks() -> List[Dict[str, Any]]:
    ensure_index()
    if not CHUNKS_PATH.exists():
        return []
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def state_summary(state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    state = state or load_state()
    return {
        "builtAt": state.get("builtAt"),
        "chunkCount": state.get("chunkCount", 0),
        "sourceCount": state.get("sourceCount", 0),
        "anchorState": state.get("anchorState", {}),
        "stale": index_stale(),
    }


def classify_route(query: str) -> str:
    lower = query.lower()
    route_scores = {route: 0 for route in ROUTE_HINTS}
    for route, hints in ROUTE_HINTS.items():
        for hint in hints:
            if hint in lower:
                route_scores[route] += 2 if " " in hint else 1
    if any(token.startswith("task-") for token in tokenize(lower)):
        route_scores["task"] += 3
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", lower):
        route_scores["history"] += 2
    if lower.strip().startswith(("what happened", "when did")):
        route_scores["history"] += 2
    best_route = max(route_scores, key=route_scores.get)
    return best_route if route_scores[best_route] > 0 else "unknown"


def route_stages(route: str) -> List[List[str]]:
    return ROUTE_STAGES.get(route, ROUTE_STAGES["unknown"])


def extract_date_bonus(chunk: Dict[str, Any]) -> float:
    if chunk.get("route") == "active":
        return 2.5

    path_name = Path(chunk["path"]).name
    match = DATE_FILE_RE.match(path_name)
    if match:
        try:
            chunk_date = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            days_away = abs((date.today() - chunk_date).days)
            return max(0.0, 2.0 - (days_away * 0.15))
        except ValueError:
            return 0.0

    updated_at = chunk.get("updated_at")
    if updated_at:
        try:
            parsed = datetime.fromisoformat(updated_at.replace("Z", "+00:00")).date()
            days_away = abs((date.today() - parsed).days)
            return max(0.0, 1.2 - (days_away * 0.08))
        except ValueError:
            return 0.0
    return 0.0


def make_snippet(content: str, query: str, max_len: int = 420) -> str:
    text = " ".join(content.split())
    if len(text) <= max_len:
        return text
    lower = text.lower()
    query_lower = query.lower().strip()
    pos = lower.find(query_lower) if query_lower else -1
    if pos < 0:
        for token in tokenize(query_lower):
            pos = lower.find(token)
            if pos >= 0:
                break
    if pos < 0:
        return text[: max_len - 1].rstrip() + "…"
    start = max(0, pos - 120)
    end = min(len(text), pos + max_len - 120)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


def score_chunk(query: str, chunk: Dict[str, Any], primary_route: str) -> Optional[Dict[str, Any]]:
    query_tokens = tokenize(query)
    if not query_tokens and not query.strip():
        return None

    title = chunk["title"].lower()
    content = chunk["content"].lower()
    source_ref = str(chunk.get("source_ref") or "").lower()

    title_hits = 0
    content_hits = 0
    partial_hits = 0
    for token in query_tokens:
        if token in title:
            title_hits += 1
        elif token in content:
            content_hits += 1
        else:
            if any(word.startswith(token) for word in tokenize(title)):
                partial_hits += 1
            elif any(word.startswith(token) for word in tokenize(content)):
                partial_hits += 1

    phrase_bonus = 0.0
    query_lower = query.lower().strip()
    if query_lower:
        if query_lower in title:
            phrase_bonus += 5.0
        elif query_lower in content:
            phrase_bonus += 3.5
        if source_ref and query_lower in source_ref:
            phrase_bonus += 6.0

    match_points = (title_hits * 5.0) + (content_hits * 2.0) + (partial_hits * 1.0) + phrase_bonus
    if match_points <= 0:
        return None

    route_bonus = 3.0 if chunk["route"] == primary_route else 0.0
    if primary_route == "protocol" and chunk.get("kind") in {"protocol_spine", "recall_map"}:
        route_bonus += 4.0
    if primary_route == "active" and query_lower in GENERIC_REANCHOR_PHRASES and chunk["route"] == "active":
        route_bonus += 5.0
    if primary_route == "task" and chunk.get("kind") == "task_anchor":
        route_bonus += 3.0
    if primary_route in {"recent", "history"} and chunk.get("kind") == "daily_anchor":
        route_bonus += 5.0
    recency_bonus = extract_date_bonus(chunk)
    score = match_points + route_bonus + recency_bonus

    result = dict(chunk)
    result["score"] = round(score, 3)
    result["snippet"] = make_snippet(chunk["content"], query)
    return result


def search_index(query: str, route: str, limit: int) -> Dict[str, Any]:
    chunks = load_chunks()
    effective_route = classify_route(query) if route == "auto" else route
    stages = route_stages(effective_route)
    results: List[Dict[str, Any]] = []
    seen: set[str] = set()
    stage_log: List[Dict[str, Any]] = []

    for stage_number, allowed_routes in enumerate(stages, start=1):
        candidates: List[Dict[str, Any]] = []
        for chunk in chunks:
            if chunk["id"] in seen or chunk["route"] not in allowed_routes:
                continue
            scored = score_chunk(query, chunk, effective_route)
            if scored is not None:
                candidates.append(scored)
        candidates.sort(key=lambda item: item["score"], reverse=True)
        stage_log.append({"stage": stage_number, "routes": allowed_routes, "hits": len(candidates)})
        for item in candidates:
            if item["id"] in seen:
                continue
            seen.add(item["id"])
            item["stage"] = stage_number
            results.append(item)
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break

    trimmed = []
    for item in results[:limit]:
        trimmed.append(
            {
                "id": item["id"],
                "title": item["title"],
                "path": item["path"],
                "route": item["route"],
                "kind": item["kind"],
                "source_ref": item.get("source_ref"),
                "score": item["score"],
                "stage": item["stage"],
                "start_line": item.get("start_line"),
                "end_line": item.get("end_line"),
                "snippet": item["snippet"],
            }
        )
    return {
        "query": query,
        "requestedRoute": route,
        "effectiveRoute": effective_route,
        "stages": stage_log,
        "results": trimmed,
        "indexState": state_summary(),
    }


def print_human_search(result: Dict[str, Any]) -> None:
    print(f"Route: {result['effectiveRoute']} (requested: {result['requestedRoute']})")
    if not result["results"]:
        print("No recall hits.")
        return
    for item in result["results"]:
        location = item["path"]
        if item.get("start_line") and item.get("end_line"):
            location += f":{item['start_line']}-{item['end_line']}"
        print(f"\n[{item['score']}] {item['title']}")
        print(f"- source: {location}")
        if item.get("source_ref"):
            print(f"- ref: {item['source_ref']}")
        print(f"- stage: {item['stage']} | route: {item['route']} | kind: {item['kind']}")
        print(f"- snippet: {item['snippet']}")


def command_build(args: argparse.Namespace) -> int:
    state = build_index()
    if args.json:
        print(json.dumps(state, indent=2))
    else:
        print(f"Built recall index: {state['chunkCount']} chunks from {state['sourceCount']} sources.")
        print(f"Built at: {state['builtAt']}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    state = load_state()
    output = {"exists": bool(state), **state_summary(state), "chunksPath": relpath(CHUNKS_PATH) if CHUNKS_PATH.exists() else None}
    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output, indent=2))
    return 0


def command_route(args: argparse.Namespace) -> int:
    route = classify_route(args.query)
    output = {"query": args.query, "route": route, "stages": route_stages(route)}
    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output, indent=2))
    return 0


def command_search(args: argparse.Namespace) -> int:
    result = search_index(args.query, args.route, args.limit)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_search(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local recall index/search for workspace memory.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_build = subparsers.add_parser("build", help="Build or rebuild the recall index.")
    p_build.add_argument("--json", action="store_true")
    p_build.set_defaults(func=command_build)

    p_status = subparsers.add_parser("status", help="Show recall index status.")
    p_status.add_argument("--json", action="store_true")
    p_status.set_defaults(func=command_status)

    p_route = subparsers.add_parser("route", help="Classify a query into a recall route.")
    p_route.add_argument("--query", required=True)
    p_route.add_argument("--json", action="store_true")
    p_route.set_defaults(func=command_route)

    p_search = subparsers.add_parser("search", help="Search the recall index.")
    p_search.add_argument("--query", required=True)
    p_search.add_argument(
        "--route",
        choices=["auto", "preference", "active", "task", "recent", "history", "protocol", "branch", "unknown"],
        default="auto",
    )
    p_search.add_argument("--limit", type=int, default=3)
    p_search.add_argument("--json", action="store_true")
    p_search.set_defaults(func=command_search)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

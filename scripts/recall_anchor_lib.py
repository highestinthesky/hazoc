#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

WORKSPACE = Path(__file__).resolve().parent.parent
ANCHOR_DIR = WORKSPACE / "tmp" / "recall-anchors"
TASK_ANCHORS_PATH = ANCHOR_DIR / "task-anchors.json"
DAILY_ANCHORS_PATH = ANCHOR_DIR / "daily-anchors.json"
TASKS_PATH = WORKSPACE / "mission-control" / "data" / "tasks.json"
MEMORY_DIR = WORKSPACE / "memory"
DATE_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}\.md$")
BULLET_RE = re.compile(r"^\s*[-*+]\s+")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    return SPACE_RE.sub(" ", (text or "").strip())


def compact(text: str, limit: int) -> str:
    text = normalize_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def iter_bullets(text: str) -> Iterable[str]:
    for raw in text.splitlines():
        if BULLET_RE.match(raw):
            bullet = BULLET_RE.sub("", raw).strip()
            if bullet:
                yield bullet


def extract_summary_fields(task: Dict[str, Any]) -> Dict[str, Any]:
    title = normalize_text(task.get("title", ""))
    notes = normalize_text(task.get("notes", ""))
    description = task.get("description", "") or ""
    bullets = []
    seen = set()
    for bullet in iter_bullets(description):
        key = bullet.lower()
        if key in seen:
            continue
        seen.add(key)
        bullets.append(compact(bullet, 180))
        if len(bullets) >= 4:
            break

    summary_candidates = [notes]
    if bullets:
        summary_candidates.extend(bullets[:2])
    summary_candidates.append(normalize_text(description))
    summary = next((compact(candidate, 260) for candidate in summary_candidates if candidate), "")

    return {
        "id": task.get("id"),
        "title": title,
        "lane": task.get("lane"),
        "updatedAt": task.get("updatedAt") or task.get("createdAt"),
        "summary": summary,
        "highlights": bullets,
        "keywords": [title, notes, task.get("id", ""), task.get("lane", "")],
    }


def build_task_anchors() -> List[Dict[str, Any]]:
    if not TASKS_PATH.exists():
        return []
    data = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    anchors = [extract_summary_fields(task) for task in data]
    anchors.sort(key=lambda item: (item.get("lane") or "", item.get("title") or ""))
    return anchors


def extract_daily_anchor(path: Path) -> Dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    headings: List[str] = []
    bullets: List[str] = []
    seen = set()

    for raw in lines:
        heading_match = HEADING_RE.match(raw)
        if heading_match:
            heading = normalize_text(heading_match.group(1))
            if heading and heading.lower() not in seen:
                seen.add(heading.lower())
                headings.append(heading)
            continue
        if BULLET_RE.match(raw):
            bullet = normalize_text(BULLET_RE.sub("", raw))
            key = bullet.lower()
            if bullet and key not in seen:
                seen.add(key)
                bullets.append(compact(bullet, 220))

    recent_bullets = bullets[-18:]
    summary = compact(" | ".join(recent_bullets[-5:]), 380)
    return {
        "date": path.stem,
        "path": str(path.relative_to(WORKSPACE)),
        "headings": headings[:8],
        "recentBullets": recent_bullets,
        "summary": summary,
        "bulletCount": len(bullets),
    }


def build_daily_anchors() -> List[Dict[str, Any]]:
    if not MEMORY_DIR.exists():
        return []
    anchors = []
    for path in sorted(MEMORY_DIR.glob("20??-??-??.md")):
        if DATE_RE.match(path.name):
            anchors.append(extract_daily_anchor(path))
    return anchors


def _write_if_changed(path: Path, payload: Any) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def build_all_anchors() -> Dict[str, Any]:
    task_anchors = build_task_anchors()
    daily_anchors = build_daily_anchors()
    task_changed = _write_if_changed(TASK_ANCHORS_PATH, task_anchors)
    daily_changed = _write_if_changed(DAILY_ANCHORS_PATH, daily_anchors)
    return {
        "taskAnchors": len(task_anchors),
        "dailyAnchors": len(daily_anchors),
        "taskAnchorsPath": str(TASK_ANCHORS_PATH.relative_to(WORKSPACE)),
        "dailyAnchorsPath": str(DAILY_ANCHORS_PATH.relative_to(WORKSPACE)),
        "taskChanged": task_changed,
        "dailyChanged": daily_changed,
    }

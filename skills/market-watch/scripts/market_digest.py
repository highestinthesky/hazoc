#!/usr/bin/env python3
"""Low-cost market-moving digest collector/compiler.

Design goals:
- keep recurring work script-only (zero model tokens by default)
- fetch a bounded allowlist of public RSS/Atom feeds
- normalize, dedupe, score, and store observations locally
- compile deterministic markdown/json digests on schedule
- install a user crontab entry for cheap recurring execution
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = SKILL_ROOT / "config"
STATE_DIR = SKILL_ROOT / "state" / "digest"
DIGESTS_DIR = STATE_DIR / "digests"
OBSERVATIONS_PATH = STATE_DIR / "observations.jsonl"
LAST_SEEN_PATH = STATE_DIR / "last_seen.json"
SOURCE_HEALTH_PATH = STATE_DIR / "source-health.json"
WORKER_STATE_PATH = STATE_DIR / "digest-worker-state.json"
LATEST_MD_PATH = STATE_DIR / "latest.md"
LATEST_JSON_PATH = STATE_DIR / "latest.json"
SOURCES_PATH = CONFIG_DIR / "digest_sources.json"
SETTINGS_PATH = CONFIG_DIR / "digest_settings.json"
DIGEST_USERS_PATH = CONFIG_DIR / "digest_users.json"
WATCHLIST_PATH = SKILL_ROOT / "state" / "watchlist.json"
USER_LATEST_DIR = STATE_DIR / "users"
WORKER_SPEC_PATH = WORKSPACE_ROOT / "workers" / "market-moving-digest-hourly" / "spec.json"
MANAGED_WORKER_STATE_PATH = WORKSPACE_ROOT / "workers" / "market-moving-digest-hourly" / "state.json"
CRON_LOG_PATH = STATE_DIR / "cron.log"
CRON_BEGIN = "# BEGIN hazoc-market-digest"
CRON_END = "# END hazoc-market-digest"
USER_AGENT = "hazoc-market-digest/1.0 (+https://docs.openclaw.ai)"

STATE_DIR.mkdir(parents=True, exist_ok=True)
DIGESTS_DIR.mkdir(parents=True, exist_ok=True)

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "to",
    "was",
    "were",
    "will",
    "with",
}

POSITIVE_WORDS = {
    "beats",
    "beat",
    "approval",
    "approved",
    "gain",
    "gains",
    "growth",
    "surge",
    "surges",
    "record",
    "raises",
    "raised",
    "expand",
    "expands",
    "strong",
    "rebound",
    "rebounds",
}

NEGATIVE_WORDS = {
    "cuts",
    "cut",
    "miss",
    "misses",
    "fall",
    "falls",
    "layoff",
    "layoffs",
    "probe",
    "probes",
    "investigation",
    "enforcement",
    "tariff",
    "tariffs",
    "sanction",
    "sanctions",
    "downgrade",
    "warns",
    "warning",
    "slump",
    "slumps",
}

SIGNAL_ADJUSTMENTS = [
    {
        "delta": -2.25,
        "patterns": [r"\bappoints?\b", r"\bappointment\b", r"named director", r"names director", r"leadership change", r"chief executive", r"executive vice president"],
    },
    {
        "delta": -1.5,
        "patterns": [r"public comment", r"comment period", r"invites? public comment", r"proposal that would allow"],
    },
    {
        "delta": -1.0,
        "patterns": [r"can it make money", r"analysis", r"what it means", r"explainer", r"fed up", r"memo to shareholders", r"what companies want", r"cramer", r"may continue to lag", r"set to open mixed"],
    },
    {
        "delta": 1.25,
        "patterns": [r"strait of hormuz", r"oil output", r"pipeline", r"production facilities", r"slashes? .*output", r"ceasefire", r"sanctions?", r"tariffs?", r"nonfarm payroll", r"consumer price index", r"producer price index", r"federal open market committee", r"fomc minutes?", r"minutes of the federal open market committee"],
    },
]

NAME_RULES = [
    {"ticker": "NVDA", "patterns": [r"\bnvidia\b"], "sector": "Semiconductors", "etfs": ["SMH", "XLK", "QQQ"], "weight": 1.5},
    {"ticker": "AMD", "patterns": [r"\bamd\b", r"advanced micro devices"], "sector": "Semiconductors", "etfs": ["SMH", "XLK", "QQQ"], "weight": 1.2},
    {"ticker": "INTC", "patterns": [r"\bintel\b"], "sector": "Semiconductors", "etfs": ["SMH", "XLK", "QQQ"], "weight": 1.0},
    {"ticker": "TSM", "patterns": [r"\btsmc\b", r"taiwan semiconductor"], "sector": "Semiconductors", "etfs": ["SMH", "XLK"], "weight": 1.2},
    {"ticker": "AAPL", "patterns": [r"\bapple\b", r"\biphone\b"], "sector": "Technology", "etfs": ["XLK", "QQQ"], "weight": 1.5},
    {"ticker": "MSFT", "patterns": [r"\bmicrosoft\b", r"\bazure\b"], "sector": "Technology", "etfs": ["XLK", "QQQ"], "weight": 1.5},
    {"ticker": "AMZN", "patterns": [r"\bamazon\b", r"\baws\b"], "sector": "Consumer / Cloud", "etfs": ["XLY", "QQQ"], "weight": 1.3},
    {"ticker": "GOOGL", "patterns": [r"\balphabet\b", r"\bgoogle\b"], "sector": "Technology / Communication Services", "etfs": ["XLC", "QQQ", "XLK"], "weight": 1.4},
    {"ticker": "META", "patterns": [r"\bmeta\b", r"\bfacebook\b", r"\binstagram\b"], "sector": "Communication Services", "etfs": ["XLC", "QQQ"], "weight": 1.2},
    {"ticker": "TSLA", "patterns": [r"\btesla\b"], "sector": "Autos / Consumer", "etfs": ["XLY", "QQQ"], "weight": 1.2},
    {"ticker": "JPM", "patterns": [r"\bjpmorgan\b", r"\bjp morgan\b"], "sector": "Financials", "etfs": ["XLF", "KBE"], "weight": 1.4},
    {"ticker": "BAC", "patterns": [r"bank of america", r"\bbac\b"], "sector": "Financials", "etfs": ["XLF", "KBE"], "weight": 1.1},
    {"ticker": "GS", "patterns": [r"goldman sachs", r"\bgs\b"], "sector": "Financials", "etfs": ["XLF", "KBE"], "weight": 1.1},
    {"ticker": "WFC", "patterns": [r"wells fargo", r"\bwfc\b"], "sector": "Financials", "etfs": ["XLF", "KBE"], "weight": 1.0},
    {"ticker": "XOM", "patterns": [r"exxon", r"exxonmobil"], "sector": "Energy", "etfs": ["XLE", "USO"], "weight": 1.1},
    {"ticker": "CVX", "patterns": [r"chevron"], "sector": "Energy", "etfs": ["XLE", "USO"], "weight": 1.0},
    {"ticker": "LLY", "patterns": [r"eli lilly", r"\blilly\b"], "sector": "Healthcare", "etfs": ["XLV", "IBB"], "weight": 1.1},
    {"ticker": "UNH", "patterns": [r"unitedhealth", r"united health"], "sector": "Healthcare", "etfs": ["XLV"], "weight": 1.0},
    {"ticker": "BA", "patterns": [r"\bboeing\b"], "sector": "Industrials", "etfs": ["XLI"], "weight": 1.0},
]

THEME_RULES = [
    {
        "id": "rates",
        "patterns": [r"fomc", r"interest rate", r"rates? decision", r"treasury yields?", r"bond yields?", r"monetary policy", r"jerome powell", r"powell", r"federal open market committee"],
        "category": "rates",
        "macroImportance": 5.0,
        "breadth": 4.0,
        "scope": "broad",
        "sectors": ["Financials", "Rate-sensitive"],
        "etfs": ["SPY", "QQQ", "TLT", "IWM", "XLF"],
    },
    {
        "id": "inflation",
        "patterns": [r"consumer price index", r"\bcpi\b", r"producer price index", r"\bppi\b", r"inflation", r"core pce", r"personal consumption expenditures"],
        "category": "inflation",
        "macroImportance": 5.0,
        "breadth": 4.0,
        "scope": "broad",
        "sectors": ["Broad market", "Consumer", "Financials"],
        "etfs": ["SPY", "QQQ", "TLT", "XLY", "XLF"],
    },
    {
        "id": "jobs",
        "patterns": [r"employment situation", r"nonfarm payroll", r"jobless claims", r"unemployment", r"labor market", r"employment cost index"],
        "category": "jobs",
        "macroImportance": 4.5,
        "breadth": 4.0,
        "scope": "broad",
        "sectors": ["Broad market", "Consumer"],
        "etfs": ["SPY", "IWM", "XLY", "TLT"],
    },
    {
        "id": "regulation",
        "patterns": [r"securities and exchange commission", r"\bsec\b", r"antitrust", r"department of justice", r"doj", r"ftc", r"regulation", r"rulemaking", r"tariffs?", r"sanctions?", r"export controls?"],
        "category": "regulation",
        "macroImportance": 3.5,
        "breadth": 3.0,
        "scope": "sector",
        "sectors": ["Financials", "Technology", "Industrials"],
        "etfs": ["XLF", "XLK", "XLI"],
    },
    {
        "id": "ai-chips",
        "patterns": [r"artificial intelligence", r"\bai\b", r"semiconductor", r"chip(s)?", r"gpu", r"foundry", r"data center"],
        "category": "ai-chips",
        "macroImportance": 2.0,
        "breadth": 1.75,
        "scope": "sector",
        "sectors": ["Technology", "Semiconductors"],
        "etfs": ["SMH", "XLK", "QQQ"],
    },
    {
        "id": "energy",
        "patterns": [r"oil", r"crude", r"opec", r"natural gas", r"energy prices?", r"refinery", r"lng"],
        "category": "energy",
        "macroImportance": 4.0,
        "breadth": 3.0,
        "scope": "sector",
        "sectors": ["Energy"],
        "etfs": ["XLE", "USO"],
    },
    {
        "id": "banks",
        "patterns": [r"bank(s|ing)?", r"capital requirements?", r"deposits?", r"lender", r"credit conditions?"],
        "category": "banks",
        "macroImportance": 3.0,
        "breadth": 2.5,
        "scope": "sector",
        "sectors": ["Financials"],
        "etfs": ["XLF", "KBE"],
    },
    {
        "id": "earnings-guidance",
        "patterns": [r"earnings", r"guidance", r"revenue", r"forecast", r"outlook", r"quarter results?", r"q[1-4] results?", r"profit"],
        "category": "earnings-guidance",
        "macroImportance": 2.5,
        "breadth": 2.0,
        "scope": "single-name",
        "sectors": ["Single company / peers"],
        "etfs": ["SPY", "QQQ"],
    },
    {
        "id": "m-and-a",
        "patterns": [r"merger", r"acquisition", r"buyout", r"takeover", r"deal talks?"],
        "category": "m-and-a",
        "macroImportance": 3.0,
        "breadth": 2.0,
        "scope": "single-name",
        "sectors": ["Single company / peers"],
        "etfs": ["SPY"],
    },
]

USER_IMPORTANCE_WEIGHTS = {
    "low": 0.8,
    "normal": 1.0,
    "high": 1.2,
    "core": 1.4,
}

NAME_RULES_BY_TICKER = {rule["ticker"]: rule for rule in NAME_RULES}
TICKER_SECTOR_HINTS = {rule["ticker"]: rule["sector"] for rule in NAME_RULES}


@dataclass
class FeedEntry:
    title: str
    link: str
    summary: str
    published_at: datetime | None
    source_name: str
    guid: str
    channel_title: str


@dataclass
class FetchResult:
    status: int
    fetched_at: str
    items: list[FeedEntry]
    etag: str | None = None
    last_modified: str | None = None
    error: str | None = None
    duration_ms: int | None = None


class MarketDigestError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(UTC).replace(microsecond=0).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)



def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)



def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    tmp.replace(path)



def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")



def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows



def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")



def load_sources() -> list[dict[str, Any]]:
    payload = read_json(SOURCES_PATH, {"sources": []})
    return [item for item in payload.get("sources", []) if item.get("enabled", True)]



def load_settings() -> dict[str, Any]:
    payload = read_json(SETTINGS_PATH, {})
    if not payload:
        raise SystemExit(f"Missing settings file: {SETTINGS_PATH}")
    return payload


def load_digest_users() -> list[dict[str, Any]]:
    payload = read_json(DIGEST_USERS_PATH, {"users": []})
    return [item for item in payload.get("users", []) if item.get("enabled", True)]


def load_watchlist_items() -> list[dict[str, Any]]:
    payload = read_json(WATCHLIST_PATH, [])
    if not isinstance(payload, list):
        return []
    items: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        ticker = str(item.get("ticker") or "").strip().upper()
        user_id = str(item.get("userId") or "").strip()
        if not ticker or not user_id:
            continue
        normalized = dict(item)
        normalized["ticker"] = ticker
        normalized["userId"] = user_id
        normalized.setdefault("aliases", [])
        normalized.setdefault("importance", "normal")
        normalized.setdefault("note", "")
        items.append(normalized)
    return items


def get_watchlist_prices(tickers: list[str]) -> tuple[dict[str, float], str | None]:
    unique = sorted({ticker.strip().upper() for ticker in tickers if ticker and ticker.strip()})
    if not unique:
        return {}, None
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    try:
        import watchlist as watchlist_module  # type: ignore

        return watchlist_module.get_prices(unique), None
    except SystemExit as exc:
        return {}, str(exc)
    except Exception as exc:  # pragma: no cover - defensive fallback
        return {}, str(exc)


def watch_item_patterns(item: dict[str, Any]) -> list[str]:
    ticker = str(item.get("ticker") or "").upper()
    patterns: list[str] = []
    rule = NAME_RULES_BY_TICKER.get(ticker)
    if rule:
        patterns.extend(rule.get("patterns", []))
    if ticker:
        patterns.append(rf"\b{re.escape(ticker)}\b")
    for alias in item.get("aliases", []) or []:
        alias = str(alias).strip()
        if alias:
            patterns.append(rf"\b{re.escape(alias)}\b")
    return patterns


def classify_digest_item_for_user(item: dict[str, Any], watch_items: list[dict[str, Any]]) -> dict[str, Any]:
    text = "\n".join([str(item.get("headline") or ""), str(item.get("summary") or "")])
    affected_names = {str(value) for value in item.get("affectedNames", [])}
    affected_etfs = {str(value) for value in item.get("affectedEtfs", [])}
    affected_sectors = {str(value) for value in item.get("affectedSectors", [])}
    matched_tickers: list[str] = []
    matched_sectors: list[str] = []
    relevance = 0.0

    for watch_item in watch_items:
        ticker = str(watch_item.get("ticker") or "").upper()
        if not ticker:
            continue
        weight = float(USER_IMPORTANCE_WEIGHTS.get(str(watch_item.get("importance") or "normal"), 1.0))
        direct_match = ticker in affected_names or ticker in affected_etfs
        if not direct_match:
            for pattern in watch_item_patterns(watch_item):
                try:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        direct_match = True
                        break
                except re.error:
                    continue
        if direct_match:
            matched_tickers.append(ticker)
            relevance += 5.0 * weight

        sector = TICKER_SECTOR_HINTS.get(ticker)
        if sector and sector in affected_sectors:
            matched_sectors.append(sector)
            relevance += 1.5 * weight

    matched_tickers = sorted(set(matched_tickers))
    matched_sectors = sorted(set(matched_sectors))
    if item.get("highPriority") and (matched_tickers or matched_sectors):
        relevance += 1.0

    scope = str(item.get("scope") or "").lower()
    sector_only_include = (
        bool(matched_sectors)
        and not matched_tickers
        and scope not in {"", "broad"}
        and (bool(item.get("highPriority")) or float(item.get("score", 0.0)) >= 10.5)
    )
    include = bool(matched_tickers) or sector_only_include
    return {
        "include": include,
        "matchedTickers": matched_tickers,
        "matchedSectors": matched_sectors,
        "userRelevance": round(relevance, 2),
    }


def build_watchlist_status(items: list[dict[str, Any]], prices: dict[str, float], checked_at: str | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in sorted(items, key=lambda row: row.get("ticker") or ""):
        ticker = str(item.get("ticker") or "").upper()
        price = prices.get(ticker)
        flags: list[str] = []
        target = item.get("target")
        stop = item.get("stop")
        if price is None:
            flags.append("price_unavailable")
        else:
            if target is not None and price >= float(target):
                flags.append("target_hit")
            if stop is not None and price <= float(stop):
                flags.append("stop_hit")
        out.append(
            {
                "ticker": ticker,
                "price": price,
                "target": target,
                "stop": stop,
                "note": item.get("note", ""),
                "importance": item.get("importance", "normal"),
                "flags": flags,
                "checkedAt": checked_at,
            }
        )
    return out


def build_user_digest_payload(
    global_payload: dict[str, Any],
    global_result: dict[str, Any],
    user: dict[str, Any],
    watch_items: list[dict[str, Any]],
    prices: dict[str, float],
    price_error: str | None,
    generated_at: str,
) -> dict[str, Any] | None:
    user_id = str(user.get("userId") or "").strip()
    if not user_id:
        return None
    if not watch_items and not user.get("watchlistEnabled", True):
        return None

    watchlist_status = build_watchlist_status(watch_items, prices, generated_at)
    matched_items: list[dict[str, Any]] = []
    for item in global_payload.get("items", []):
        if not isinstance(item, dict):
            continue
        match = classify_digest_item_for_user(item, watch_items)
        if not match["include"]:
            continue
        merged = dict(item)
        merged.update(match)
        matched_items.append(merged)
    matched_items.sort(key=lambda row: (float(row.get("userRelevance", 0.0)), float(row.get("score", 0.0))), reverse=True)
    matched_items = matched_items[:6]

    return {
        "kind": "user-watchlist-digest",
        "userId": user_id,
        "displayName": user.get("displayName") or user_id,
        "generatedAt": generated_at,
        "timezone": user.get("timezone") or global_payload.get("timezone") or "America/New_York",
        "windowId": global_payload.get("windowId"),
        "label": global_payload.get("label"),
        "globalGeneratedAt": global_payload.get("generatedAt"),
        "globalWindowStart": global_payload.get("windowStart"),
        "globalWindowEnd": global_payload.get("windowEnd"),
        "globalDigestPathMd": global_result.get("pathMd"),
        "globalDigestPathJson": global_result.get("pathJson"),
        "deliveryOrder": ["global", "user"],
        "watchlist": [item.get("ticker") for item in watch_items],
        "watchlistStatus": watchlist_status,
        "watchFlags": sum(1 for item in watchlist_status if item.get("flags")),
        "priceError": price_error,
        "matchedItems": matched_items,
        "matchedItemCount": len(matched_items),
    }


def user_digest_output_paths(payload: dict[str, Any]) -> tuple[Path, Path]:
    generated = parse_datetime_maybe(payload.get("generatedAt")) or utc_now()
    day_dir = DIGESTS_DIR / generated.date().isoformat()
    day_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{payload['windowId']}--user--{payload['userId']}"
    return day_dir / f"{stem}.md", day_dir / f"{stem}.json"


def render_user_digest_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Market digest — {payload['displayName']} watchlist — {payload['label']}")
    lines.append("")
    lines.append(f"- Generated: {payload['generatedAt']}")
    lines.append(f"- Follows global digest: {payload.get('globalDigestPathMd')}")
    lines.append(f"- Global window: {payload.get('globalWindowStart')} → {payload.get('globalWindowEnd')}")
    lines.append(f"- Watched tickers: {', '.join(payload.get('watchlist', [])) or 'none'}")
    if payload.get("priceError"):
        lines.append(f"- Price status: unavailable ({payload['priceError']})")
    lines.append("")

    lines.append("## Watchlist status")
    if not payload.get("watchlistStatus"):
        lines.append("- No watchlist items configured.")
    else:
        for item in payload.get("watchlistStatus", []):
            flags = ", ".join(item.get("flags", [])) if item.get("flags") else "none"
            lines.append(
                f"- {item['ticker']}: price={item.get('price')} | importance={item.get('importance')} | flags={flags}"
            )
    lines.append("")

    lines.append("## Relevant items")
    matched_items = payload.get("matchedItems", [])
    if not matched_items:
        lines.append("- No current global-digest items crossed the watchlist relevance threshold.")
    else:
        for idx, item in enumerate(matched_items, start=1):
            lines.append(f"### {idx}. {item['headline']}")
            match_bits: list[str] = []
            if item.get("matchedTickers"):
                match_bits.append(f"tickers={', '.join(item['matchedTickers'])}")
            if item.get("matchedSectors"):
                match_bits.append(f"sectors={', '.join(item['matchedSectors'])}")
            lines.append(f"- Match basis: {' | '.join(match_bits) if match_bits else 'general overlap'}")
            lines.append(f"- Why it matters: {item['whyItMatters']}")
            lines.append(
                f"- Scope: {item['scope']} | Confidence: {item['confidenceLabel']} ({item['confidence']}) | Direction: {item['direction']} | Score: {item['score']} | User relevance: {item['userRelevance']}"
            )
            lines.append(f"- Source: {item['source']} — {item['url']}")
            if item.get("summary"):
                lines.append(f"- Summary: {item['summary']}")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def write_user_digest(payload: dict[str, Any], worker_state: dict[str, Any]) -> dict[str, Any]:
    md_path, json_path = user_digest_output_paths(payload)
    markdown = render_user_digest_markdown(payload)
    ensure_parent(md_path)
    md_path.write_text(markdown, encoding="utf-8")
    write_json(json_path, payload)

    latest_dir = USER_LATEST_DIR / str(payload["userId"])
    latest_dir.mkdir(parents=True, exist_ok=True)
    (latest_dir / "latest.md").write_text(markdown, encoding="utf-8")
    write_json(latest_dir / "latest.json", payload)

    worker_state.setdefault("lastUserDigests", {}).setdefault(payload["windowId"], {})[payload["userId"]] = {
        "windowId": payload["windowId"],
        "userId": payload["userId"],
        "generatedAt": payload["generatedAt"],
        "matchedItemCount": payload.get("matchedItemCount", 0),
        "pathMd": str(md_path.relative_to(WORKSPACE_ROOT)),
        "pathJson": str(json_path.relative_to(WORKSPACE_ROOT)),
        "globalDigestPathMd": payload.get("globalDigestPathMd"),
    }
    return {
        "userId": payload["userId"],
        "generatedAt": payload["generatedAt"],
        "matchedItems": payload.get("matchedItemCount", 0),
        "pathMd": str(md_path.relative_to(WORKSPACE_ROOT)),
        "pathJson": str(json_path.relative_to(WORKSPACE_ROOT)),
    }


def generate_user_digests_for_global(global_result: dict[str, Any]) -> list[dict[str, Any]]:
    if not global_result.get("generated"):
        return []
    path_json = global_result.get("pathJson")
    if not path_json:
        return []
    global_payload = read_json(WORKSPACE_ROOT / path_json, None)
    if not isinstance(global_payload, dict):
        return []

    users = [user for user in load_digest_users() if user.get("watchlistEnabled", True)]
    if not users:
        return []
    watch_items = load_watchlist_items()
    watch_by_user: dict[str, list[dict[str, Any]]] = {}
    for item in watch_items:
        watch_by_user.setdefault(str(item.get("userId") or ""), []).append(item)
    union_tickers = [item["ticker"] for item in watch_items if item.get("userId") in {user.get("userId") for user in users}]
    prices, price_error = get_watchlist_prices(union_tickers)
    generated_at = iso(utc_now()) or ""

    worker_state = load_worker_state()
    results: list[dict[str, Any]] = []
    for user in users:
        user_id = str(user.get("userId") or "").strip()
        if not user_id:
            continue
        payload = build_user_digest_payload(
            global_payload,
            global_result,
            user,
            watch_by_user.get(user_id, []),
            prices,
            price_error,
            generated_at,
        )
        if payload is None:
            continue
        results.append(write_user_digest(payload, worker_state))

    if results:
        worker_state["lastFanoutAt"] = generated_at
        write_json(WORKER_STATE_PATH, worker_state)
        sync_managed_worker_state(worker_state)
    return results



def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]



def strip_tags(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()



def normalize_text(value: str) -> str:
    value = html.unescape(value or "").lower()
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()



def significant_tokens(value: str) -> set[str]:
    tokens = [token for token in normalize_text(value).split() if len(token) >= 3 and token not in STOPWORDS]
    return set(tokens)



def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    if union == 0:
        return 0.0
    return inter / union



def parse_datetime_maybe(raw: str | None) -> datetime | None:
    if not raw:
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        dt = parsedate_to_datetime(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except Exception:
        return None



def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlsplit(url)
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [(k, v) for (k, v) in query_pairs if not k.lower().startswith("utm_")]
    query = urllib.parse.urlencode(filtered)
    clean = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path, query, ""))
    return clean



def feed_item_text(node: ET.Element, field: str) -> str:
    for child in node.iter():
        if local_name(child.tag) == field and (child.text or "").strip():
            return child.text or ""
    return ""



def parse_feed(xml_text: str) -> tuple[str, list[FeedEntry]]:
    root = ET.fromstring(xml_text)
    root_name = local_name(root.tag)

    channel_title = ""
    items: list[FeedEntry] = []

    if root_name == "rss":
        channel = next((child for child in root if local_name(child.tag) == "channel"), None)
        if channel is None:
            return channel_title, items
        channel_title = feed_item_text(channel, "title")
        for item in channel:
            if local_name(item.tag) != "item":
                continue
            title = strip_tags(feed_item_text(item, "title"))
            link = strip_tags(feed_item_text(item, "link"))
            summary = strip_tags(feed_item_text(item, "description"))
            guid = strip_tags(feed_item_text(item, "guid")) or link or title
            source_name = strip_tags(feed_item_text(item, "source")) or channel_title or "Unknown source"
            published = parse_datetime_maybe(feed_item_text(item, "pubDate") or feed_item_text(item, "published") or feed_item_text(item, "updated"))
            if channel_title.lower().startswith("google news") and " - " in title:
                main_title, guessed_source = title.rsplit(" - ", 1)
                title = main_title.strip()
                if guessed_source.strip():
                    source_name = guessed_source.strip()
            if title and link:
                items.append(FeedEntry(title=title, link=link, summary=summary, published_at=published, source_name=source_name, guid=guid, channel_title=channel_title or "RSS"))
        return channel_title, items

    if root_name == "feed":
        channel_title = feed_item_text(root, "title")
        for entry in root:
            if local_name(entry.tag) != "entry":
                continue
            title = strip_tags(feed_item_text(entry, "title"))
            summary = strip_tags(feed_item_text(entry, "summary") or feed_item_text(entry, "content"))
            link = ""
            for link_node in entry.iter():
                if local_name(link_node.tag) != "link":
                    continue
                href = (link_node.attrib.get("href") or "").strip()
                rel = (link_node.attrib.get("rel") or "alternate").strip()
                if href and rel in {"alternate", "self", ""}:
                    link = href
                    break
            guid = strip_tags(feed_item_text(entry, "id")) or link or title
            source_name = channel_title or "Atom feed"
            published = parse_datetime_maybe(feed_item_text(entry, "updated") or feed_item_text(entry, "published"))
            if title and link:
                items.append(FeedEntry(title=title, link=link, summary=summary, published_at=published, source_name=source_name, guid=guid, channel_title=channel_title or "Atom"))
        return channel_title, items

    raise MarketDigestError(f"Unsupported feed root: {root.tag}")



def fetch_feed(source: dict[str, Any], cached_health: dict[str, Any], timeout_seconds: int) -> FetchResult:
    started = utc_now()
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/xml, text/xml, text/html;q=0.8, */*;q=0.5",
    }
    etag = (cached_health or {}).get("etag")
    last_modified = (cached_health or {}).get("lastModified")
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified

    request = urllib.request.Request(source["url"], headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status = getattr(response, "status", 200)
            if status == 304:
                return FetchResult(status=304, fetched_at=iso(utc_now()) or "", items=[], etag=etag, last_modified=last_modified, duration_ms=int((utc_now() - started).total_seconds() * 1000))
            raw = response.read()
            encoding = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(encoding, errors="replace")
            _, items = parse_feed(text)
            return FetchResult(
                status=status,
                fetched_at=iso(utc_now()) or "",
                items=items,
                etag=response.headers.get("ETag") or etag,
                last_modified=response.headers.get("Last-Modified") or last_modified,
                duration_ms=int((utc_now() - started).total_seconds() * 1000),
            )
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            return FetchResult(status=304, fetched_at=iso(utc_now()) or "", items=[], etag=etag, last_modified=last_modified, duration_ms=int((utc_now() - started).total_seconds() * 1000))
        return FetchResult(status=exc.code, fetched_at=iso(utc_now()) or "", items=[], etag=etag, last_modified=last_modified, error=f"HTTP {exc.code}: {exc.reason}", duration_ms=int((utc_now() - started).total_seconds() * 1000))
    except Exception as exc:
        return FetchResult(status=0, fetched_at=iso(utc_now()) or "", items=[], etag=etag, last_modified=last_modified, error=str(exc), duration_ms=int((utc_now() - started).total_seconds() * 1000))



def in_recent_window(published_at: datetime | None, now_utc: datetime, lookback_hours: int) -> bool:
    if published_at is None:
        return True
    return published_at >= (now_utc - timedelta(hours=lookback_hours))



def infer_names_and_sectors(text: str) -> tuple[list[str], list[str], list[str], float]:
    names: list[str] = []
    sectors: list[str] = []
    etfs: list[str] = []
    significance = 0.0
    for rule in NAME_RULES:
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in rule["patterns"]):
            names.append(rule["ticker"])
            sectors.append(rule["sector"])
            etfs.extend(rule["etfs"])
            significance += float(rule["weight"])
    return sorted(set(names)), sorted(set(sectors)), sorted(set(etfs)), round(significance, 2)



def infer_themes(text: str) -> tuple[list[str], str, float, float, str, list[str], list[str]]:
    matched: list[dict[str, Any]] = []
    for rule in THEME_RULES:
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in rule["patterns"]):
            matched.append(rule)

    if not matched:
        return [], "general-market", 0.5, 0.5, "single-name", [], []

    category = matched[0]["category"]
    macro_importance = max(float(rule["macroImportance"]) for rule in matched)
    breadth = max(float(rule["breadth"]) for rule in matched)
    scope_order = {"single-name": 1, "sector": 2, "broad": 3}
    scope = max((rule["scope"] for rule in matched), key=lambda value: scope_order.get(value, 0))
    sectors = sorted({sector for rule in matched for sector in rule.get("sectors", [])})
    etfs = sorted({etf for rule in matched for etf in rule.get("etfs", [])})
    return [rule["id"] for rule in matched], category, macro_importance, breadth, scope, sectors, etfs



def infer_direction(text: str) -> str:
    tokens = significant_tokens(text)
    positive = len(tokens & POSITIVE_WORDS)
    negative = len(tokens & NEGATIVE_WORDS)
    if positive > negative:
        return "positive"
    if negative > positive:
        return "negative"
    if positive == negative == 0:
        return "unclear"
    return "mixed"



def novelty_score(published_at: datetime | None, now_utc: datetime) -> float:
    if published_at is None:
        return 1.5
    age = max((now_utc - published_at).total_seconds() / 3600.0, 0.0)
    if age <= 3:
        return 2.5
    if age <= 12:
        return 2.0
    if age <= 24:
        return 1.5
    return 1.0



def source_quality(source_tier: int) -> float:
    if source_tier <= 1:
        return 3.5
    if source_tier == 2:
        return 2.5
    return 1.5



def signal_adjustment(text: str) -> float:
    adjustment = 0.0
    for rule in SIGNAL_ADJUSTMENTS:
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in rule["patterns"]):
            adjustment += float(rule["delta"])
    return round(adjustment, 2)



def confidence_score(source_tier: int, theme_count: int, confirmation_count: int) -> float:
    base = 0.52 + (0.1 if source_tier <= 1 else 0.04)
    base += min(theme_count, 3) * 0.06
    base += min(max(confirmation_count - 1, 0), 2) * 0.08
    return round(min(base, 0.95), 2)



def make_dedupe_key(source_id: str, title: str, url: str) -> str:
    canonical = f"{source_id}|{normalize_text(title)}|{canonicalize_url(url)}"
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]



def observation_id(source_id: str, title: str, url: str, published_at: datetime | None) -> str:
    base = f"{source_id}|{title}|{canonicalize_url(url)}|{iso(published_at) or ''}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]



def entry_allowed(source: dict[str, Any], entry: FeedEntry) -> bool:
    haystack = "\n".join([entry.title or "", entry.summary or "", entry.link or "", entry.source_name or ""])
    include_patterns = source.get("includePatterns", []) or []
    exclude_patterns = source.get("excludePatterns", []) or []
    if include_patterns and not any(re.search(pattern, haystack, flags=re.IGNORECASE) for pattern in include_patterns):
        return False
    if exclude_patterns and any(re.search(pattern, haystack, flags=re.IGNORECASE) for pattern in exclude_patterns):
        return False
    return True



def build_observation(source: dict[str, Any], entry: FeedEntry, now_utc: datetime) -> dict[str, Any]:
    text = f"{entry.title}\n{entry.summary}"
    normalized = normalize_text(text)
    matched_themes, inferred_category, macro_importance, breadth, scope, theme_sectors, theme_etfs = infer_themes(normalized)
    names, name_sectors, name_etfs, affected_name_significance = infer_names_and_sectors(normalized)

    sectors = sorted(set(theme_sectors + name_sectors))
    etfs = sorted(set(theme_etfs + name_etfs))
    direction = infer_direction(normalized)
    tier = int(source.get("sourceTier", 2))
    novelty = novelty_score(entry.published_at, now_utc)
    quality = source_quality(tier)
    adjustment = signal_adjustment(normalized)
    score = (
        macro_importance
        + breadth
        + novelty
        + quality
        + affected_name_significance
        + float(source.get("scoreBoost", 0.0) or 0.0)
        + adjustment
    )
    category = inferred_category if inferred_category != "general-market" else source.get("defaultCategory", inferred_category)

    return {
        "id": observation_id(source["id"], entry.title, entry.link, entry.published_at),
        "seenAt": iso(now_utc),
        "eventTime": iso(entry.published_at),
        "source": entry.source_name or source.get("label", source["id"]),
        "sourceId": source["id"],
        "sourceFeed": source.get("label", source["id"]),
        "sourceTier": tier,
        "headline": entry.title,
        "url": canonicalize_url(entry.link),
        "summary": entry.summary,
        "category": category,
        "themes": matched_themes,
        "macroImportance": round(macro_importance, 2),
        "novelty": round(novelty, 2),
        "breadth": round(breadth, 2),
        "sourceQuality": round(quality, 2),
        "confirmationCount": 1,
        "affectedSectors": sectors,
        "affectedNames": names,
        "affectedEtfs": etfs,
        "affectedNameSignificance": round(affected_name_significance, 2),
        "signalAdjustment": round(adjustment, 2),
        "direction": direction,
        "confidence": confidence_score(tier, len(matched_themes), 1),
        "digestEligible": False,
        "dedupeKey": make_dedupe_key(source["id"], entry.title, entry.link),
        "scope": scope,
        "score": round(score, 2),
        "sourceTags": source.get("tags", []),
        "guid": entry.guid,
        "channelTitle": entry.channel_title,
    }



def match_recent_confirmation(candidate: dict[str, Any], others: list[dict[str, Any]], recent_hours: int, now_utc: datetime) -> int:
    candidate_tokens = significant_tokens(candidate.get("headline", ""))
    if not candidate_tokens:
        return 1
    threshold = now_utc - timedelta(hours=recent_hours)
    count = 1
    seen_sources = {candidate.get("sourceId")}
    for other in others:
        if other.get("sourceId") in seen_sources:
            continue
        event_time = parse_datetime_maybe(other.get("eventTime") or other.get("seenAt"))
        if event_time and event_time < threshold:
            continue
        similarity = jaccard(candidate_tokens, significant_tokens(other.get("headline", "")))
        if similarity >= 0.6:
            count += 1
            seen_sources.add(other.get("sourceId"))
    return min(count, 4)



def compute_digest_eligibility(observation: dict[str, Any], min_digest_score: float, high_priority_score: float) -> dict[str, Any]:
    confirmation_bonus = max(observation.get("confirmationCount", 1) - 1, 0) * 0.75
    final_score = round(float(observation.get("score", 0.0)) + confirmation_bonus, 2)
    observation["score"] = final_score
    observation["confidence"] = confidence_score(int(observation.get("sourceTier", 2)), len(observation.get("themes", [])), int(observation.get("confirmationCount", 1)))
    observation["digestEligible"] = final_score >= min_digest_score
    observation["highPriority"] = final_score >= high_priority_score
    return observation



def prune_last_seen(last_seen: dict[str, Any], ttl_days: int, now_utc: datetime) -> dict[str, Any]:
    cutoff = now_utc - timedelta(days=ttl_days)
    keys: dict[str, str] = last_seen.get("keys", {}) if isinstance(last_seen, dict) else {}
    pruned = {
        key: value
        for key, value in keys.items()
        if (parse_datetime_maybe(value) or cutoff) >= cutoff
    }
    return {"keys": pruned, "updatedAt": iso(now_utc)}



def prune_observations(rows: list[dict[str, Any]], retention_days: int, max_rows: int, now_utc: datetime) -> list[dict[str, Any]]:
    cutoff = now_utc - timedelta(days=retention_days)
    kept = []
    for row in rows:
        observed_at = parse_datetime_maybe(row.get("seenAt") or row.get("eventTime"))
        if observed_at and observed_at < cutoff:
            continue
        kept.append(row)
    if len(kept) > max_rows:
        kept = kept[-max_rows:]
    return kept



def why_it_matters(observation: dict[str, Any]) -> str:
    themes = observation.get("themes", [])
    scope = observation.get("scope", "single-name")
    sectors = observation.get("affectedSectors", [])
    names = observation.get("affectedNames", [])
    if any(theme in themes for theme in ["rates", "inflation", "jobs"]):
        return "Broad-market potential because it can shift expectations around rates, growth, inflation, or policy."
    if "energy" in themes:
        return "Energy-supply or pricing signal that can spill into inflation expectations, energy equities, and broad risk sentiment."
    if "regulation" in themes:
        if sectors:
            return f"Regulatory/policy signal that could matter beyond one headline, especially for {', '.join(sectors[:3])}."
        return "Regulatory/policy signal that can reprice affected sectors quickly if it changes compliance, enforcement, or capital expectations."
    if "ai-chips" in themes and names:
        return f"Tech/AI signal most relevant to {', '.join(names[:3])} and nearby semis/platform peers."
    if scope == "sector" and sectors:
        return f"Most relevant to {', '.join(sectors[:3])} because it may change the near-term outlook for that slice of the market."
    if names:
        return f"Mostly company-specific, but notable enough to matter for {', '.join(names[:3])} and nearby peers/ETFs."
    return "Potentially relevant market signal; ranked here because it cleared the local significance threshold."



def confidence_label(value: float) -> str:
    if value >= 0.82:
        return "high"
    if value >= 0.68:
        return "medium"
    return "low"



def load_worker_state() -> dict[str, Any]:
    return read_json(
        WORKER_STATE_PATH,
        {
            "lastCollectAt": None,
            "lastCollectSummary": {},
            "lastDigests": {},
            "installedCron": False,
            "lastRunAt": None,
            "lastRunMode": None,
        },
    )



def sync_managed_worker_state(worker_state: dict[str, Any]) -> None:
    payload = read_json(
        MANAGED_WORKER_STATE_PATH,
        {
            "workerId": "market-moving-digest-hourly",
            "status": "idle",
            "lastRunAt": None,
            "lastCollectAt": None,
            "lastDigestAt": None,
            "lastDigestWindow": None,
            "observationsStored": 0,
            "lastError": None,
        },
    )
    payload["lastRunAt"] = worker_state.get("lastRunAt")
    payload["lastCollectAt"] = worker_state.get("lastCollectAt")
    last_digests = worker_state.get("lastDigests", {})
    latest_digest = None
    if last_digests:
        latest_digest = max(last_digests.values(), key=lambda item: item.get("generatedAt") or "")
    payload["lastDigestAt"] = latest_digest.get("generatedAt") if latest_digest else None
    payload["lastDigestWindow"] = latest_digest.get("windowId") if latest_digest else None
    payload["observationsStored"] = int(worker_state.get("observationCount") or 0)
    payload["installedCron"] = bool(worker_state.get("installedCron"))
    payload["status"] = "healthy"
    payload["lastError"] = None
    write_json(MANAGED_WORKER_STATE_PATH, payload)



def update_worker_state(worker_state: dict[str, Any], *, mode: str, now_utc: datetime) -> None:
    worker_state["lastRunAt"] = iso(now_utc)
    worker_state["lastRunMode"] = mode



def collect_observations(args: argparse.Namespace) -> dict[str, Any]:
    now_utc = utc_now()
    settings = load_settings()
    scoring = settings.get("scoring", {})
    collection_settings = settings.get("collection", {})
    timeout_seconds = int(collection_settings.get("httpTimeoutSeconds", 20))
    min_digest_score = float(scoring.get("minDigestEligibleScore", 7.0))
    high_priority_score = float(scoring.get("highPriorityScore", 11.0))
    recent_similarity_hours = int(scoring.get("recentSimilarityHours", 18))
    ttl_days = int(scoring.get("dedupeTtlDays", 14))
    retention_days = int(scoring.get("retentionDays", 14))
    max_rows = int(scoring.get("maxStoredObservations", 3000))

    sources = load_sources()
    last_seen = read_json(LAST_SEEN_PATH, {"keys": {}, "updatedAt": None})
    seen_keys: dict[str, str] = dict(last_seen.get("keys", {}))
    source_health = read_json(SOURCE_HEALTH_PATH, {})
    existing_rows = read_jsonl(OBSERVATIONS_PATH)

    new_rows: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []

    for source in sources:
        cached = source_health.get(source["id"], {}) if isinstance(source_health, dict) else {}
        result = fetch_feed(source, cached, timeout_seconds)
        source_summary = {
            "sourceId": source["id"],
            "label": source.get("label", source["id"]),
            "status": result.status,
            "fetchedAt": result.fetched_at,
            "fetchedItems": len(result.items),
            "acceptedItems": 0,
            "error": result.error,
        }
        source_health[source["id"]] = {
            "label": source.get("label", source["id"]),
            "status": result.status,
            "fetchedAt": result.fetched_at,
            "fetchedItems": len(result.items),
            "etag": result.etag,
            "lastModified": result.last_modified,
            "error": result.error,
            "durationMs": result.duration_ms,
        }
        if result.status not in {0, 200, 304}:
            source_summaries.append(source_summary)
            continue
        for entry in result.items[: int(source.get("maxItems") or collection_settings.get("maxItemsPerSourceDefault", 12))]:
            if not in_recent_window(entry.published_at, now_utc, int(source.get("lookbackHours", 48))):
                continue
            if not entry_allowed(source, entry):
                continue
            dedupe_key = make_dedupe_key(source["id"], entry.title, entry.link)
            if dedupe_key in seen_keys:
                continue
            observation = build_observation(source, entry, now_utc)
            new_rows.append(observation)
            seen_keys[dedupe_key] = iso(now_utc) or ""
            source_summary["acceptedItems"] += 1
        source_summaries.append(source_summary)

    recent_existing = prune_observations(existing_rows, retention_days, max_rows, now_utc)
    context_rows = recent_existing[-200:] + new_rows
    finalized_rows: list[dict[str, Any]] = []
    for row in new_rows:
        confirmation = match_recent_confirmation(row, [candidate for candidate in context_rows if candidate.get("id") != row.get("id")], recent_similarity_hours, now_utc)
        row["confirmationCount"] = confirmation
        finalized_rows.append(compute_digest_eligibility(row, min_digest_score, high_priority_score))

    if finalized_rows:
        merged_rows = recent_existing + finalized_rows
    else:
        merged_rows = recent_existing
    merged_rows = prune_observations(merged_rows, retention_days, max_rows, now_utc)

    write_jsonl(OBSERVATIONS_PATH, merged_rows)
    write_json(LAST_SEEN_PATH, prune_last_seen({"keys": seen_keys}, ttl_days, now_utc))
    write_json(SOURCE_HEALTH_PATH, source_health)

    worker_state = load_worker_state()
    worker_state["lastCollectAt"] = iso(now_utc)
    worker_state["lastCollectSummary"] = {
        "newObservations": len(finalized_rows),
        "digestEligible": sum(1 for row in finalized_rows if row.get("digestEligible")),
        "highPriority": sum(1 for row in finalized_rows if row.get("highPriority")),
        "sourcesChecked": len(sources),
        "sourceSummaries": source_summaries,
    }
    worker_state["observationCount"] = len(merged_rows)
    update_worker_state(worker_state, mode="collect", now_utc=now_utc)
    write_json(WORKER_STATE_PATH, worker_state)
    sync_managed_worker_state(worker_state)

    summary = {
        "collectedAt": iso(now_utc),
        "sourcesChecked": len(sources),
        "newObservations": len(finalized_rows),
        "digestEligible": sum(1 for row in finalized_rows if row.get("digestEligible")),
        "highPriority": sum(1 for row in finalized_rows if row.get("highPriority")),
        "sourceSummaries": source_summaries,
    }
    return summary



def local_now(settings: dict[str, Any], now_utc: datetime | None = None) -> datetime:
    tz = ZoneInfo(settings.get("timezone", "America/New_York"))
    return (now_utc or utc_now()).astimezone(tz)



def due_digest_windows(settings: dict[str, Any], worker_state: dict[str, Any], now_utc: datetime) -> list[dict[str, Any]]:
    now_local = local_now(settings, now_utc)
    weekday = now_local.isoweekday()
    allowed_weekdays = set(settings.get("collection", {}).get("weekdays", [1, 2, 3, 4, 5]))
    if weekday not in allowed_weekdays:
        return []

    due: list[dict[str, Any]] = []
    last_digests = worker_state.get("lastDigests", {})
    for window in settings.get("digestWindows", []):
        scheduled_local = now_local.replace(hour=int(window["hour"]), minute=int(window["minute"]), second=0, microsecond=0)
        if now_local < scheduled_local:
            continue
        last_info = last_digests.get(window["id"], {})
        generated_at = parse_datetime_maybe(last_info.get("generatedAt"))
        if generated_at and generated_at.astimezone(now_local.tzinfo).date() == now_local.date():
            continue
        due.append(window)
    return due



def dedupe_digest_rows(rows: list[dict[str, Any]], max_items: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    category_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    for row in rows:
        category = row.get("category", "unknown")
        source_id = row.get("sourceId", "unknown")
        if category_counts[category] >= 3:
            continue
        if source_counts[source_id] >= 3:
            continue
        row_tokens = significant_tokens(row.get("headline", ""))
        duplicate = False
        for chosen in selected:
            chosen_tokens = significant_tokens(chosen.get("headline", ""))
            similarity = jaccard(row_tokens, chosen_tokens)
            shared_themes = set(row.get("themes", [])) & set(chosen.get("themes", []))
            if similarity >= 0.58:
                duplicate = True
                break
            if shared_themes and len(row_tokens & chosen_tokens) >= 3:
                duplicate = True
                break
        if duplicate:
            continue
        selected.append(row)
        category_counts[category] += 1
        source_counts[source_id] += 1
        if len(selected) >= max_items:
            break
    return selected



def observations_for_window(window: dict[str, Any], settings: dict[str, Any], worker_state: dict[str, Any], now_utc: datetime) -> tuple[datetime, datetime, list[dict[str, Any]]]:
    all_rows = read_jsonl(OBSERVATIONS_PATH)
    last_info = (worker_state.get("lastDigests", {}) or {}).get(window["id"], {})
    generated_at = parse_datetime_maybe(last_info.get("generatedAt"))
    if generated_at is None:
        window_start = now_utc - timedelta(hours=float(window.get("lookbackHours", 4)))
    else:
        window_start = generated_at
    window_end = now_utc
    rows = []
    for row in all_rows:
        seen_at = parse_datetime_maybe(row.get("seenAt") or row.get("eventTime"))
        if seen_at is None:
            continue
        if seen_at <= window_start or seen_at > window_end:
            continue
        if not row.get("digestEligible"):
            continue
        rows.append(row)
    rows.sort(key=lambda row: (float(row.get("score", 0.0)), row.get("eventTime") or row.get("seenAt") or ""), reverse=True)
    max_items = int(settings.get("scoring", {}).get("maxItemsPerDigest", 10))
    return window_start, window_end, dedupe_digest_rows(rows, max_items)



def build_digest_payload(window: dict[str, Any], settings: dict[str, Any], worker_state: dict[str, Any], now_utc: datetime) -> dict[str, Any] | None:
    window_start, window_end, rows = observations_for_window(window, settings, worker_state, now_utc)
    min_items = int(window.get("minimumItems", 1))
    min_total_score = float(window.get("minimumTotalScore", 0.0))
    total_score = round(sum(float(row.get("score", 0.0)) for row in rows), 2)
    high_priority_count = sum(1 for row in rows if row.get("highPriority"))
    if not rows:
        return None
    if len(rows) < min_items and high_priority_count == 0:
        return None
    if total_score < min_total_score and high_priority_count == 0:
        return None

    top_categories = Counter(row.get("category", "unknown") for row in rows).most_common(5)
    low_confidence = [row for row in rows if float(row.get("confidence", 0.0)) < 0.68]
    payload = {
        "windowId": window["id"],
        "label": window["label"],
        "generatedAt": iso(now_utc),
        "timezone": settings.get("timezone", "America/New_York"),
        "windowStart": iso(window_start),
        "windowEnd": iso(window_end),
        "totalItems": len(rows),
        "totalScore": total_score,
        "highPriorityCount": high_priority_count,
        "topCategories": [{"category": category, "count": count} for category, count in top_categories],
        "unresolvedUncertainties": [row["headline"] for row in low_confidence[:5]],
        "items": [],
    }
    for row in rows:
        payload["items"].append(
            {
                "headline": row["headline"],
                "whyItMatters": why_it_matters(row),
                "affectedSectors": row.get("affectedSectors", []),
                "affectedNames": row.get("affectedNames", []),
                "affectedEtfs": row.get("affectedEtfs", []),
                "scope": row.get("scope", "single-name"),
                "confidence": row.get("confidence"),
                "confidenceLabel": confidence_label(float(row.get("confidence", 0.0))),
                "direction": row.get("direction", "unclear"),
                "score": row.get("score"),
                "highPriority": row.get("highPriority", False),
                "themes": row.get("themes", []),
                "category": row.get("category"),
                "source": row.get("source"),
                "url": row.get("url"),
                "summary": row.get("summary"),
                "eventTime": row.get("eventTime"),
            }
        )
    return payload



def render_digest_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Market digest — {payload['label']}")
    lines.append("")
    lines.append(f"- Generated: {payload['generatedAt']}")
    lines.append(f"- Window: {payload['windowStart']} → {payload['windowEnd']}")
    lines.append(f"- Items: {payload['totalItems']}")
    lines.append(f"- Total score: {payload['totalScore']}")
    if payload.get("topCategories"):
        top_categories = ", ".join(f"{item['category']} ({item['count']})" for item in payload["topCategories"])
        lines.append(f"- Top categories: {top_categories}")
    lines.append("")
    if payload.get("unresolvedUncertainties"):
        lines.append("## Unresolved uncertainties")
        for item in payload["unresolvedUncertainties"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("## Items")
    lines.append("")
    for idx, item in enumerate(payload.get("items", []), start=1):
        lines.append(f"### {idx}. {item['headline']}")
        lines.append(f"- Why it matters: {item['whyItMatters']}")
        affected = []
        if item.get("affectedSectors"):
            affected.append(f"sectors={', '.join(item['affectedSectors'])}")
        if item.get("affectedNames"):
            affected.append(f"names={', '.join(item['affectedNames'])}")
        if item.get("affectedEtfs"):
            affected.append(f"ETFs={', '.join(item['affectedEtfs'])}")
        if affected:
            lines.append(f"- Likely affected: {' | '.join(affected)}")
        lines.append(f"- Scope: {item['scope']} | Confidence: {item['confidenceLabel']} ({item['confidence']}) | Direction: {item['direction']} | Score: {item['score']}")
        lines.append(f"- Source: {item['source']} — {item['url']}")
        if item.get("summary"):
            lines.append(f"- Summary: {item['summary']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"



def digest_output_paths(payload: dict[str, Any]) -> tuple[Path, Path]:
    generated = parse_datetime_maybe(payload["generatedAt"]) or utc_now()
    day_dir = DIGESTS_DIR / generated.date().isoformat()
    day_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{payload['windowId']}"
    return day_dir / f"{stem}.md", day_dir / f"{stem}.json"



def write_digest(payload: dict[str, Any], settings: dict[str, Any], worker_state: dict[str, Any], now_utc: datetime) -> dict[str, Any]:
    md_path, json_path = digest_output_paths(payload)
    markdown = render_digest_markdown(payload)
    ensure_parent(md_path)
    md_path.write_text(markdown, encoding="utf-8")
    write_json(json_path, payload)
    if settings.get("delivery", {}).get("writeLatestCopies", True):
        LATEST_MD_PATH.write_text(markdown, encoding="utf-8")
        write_json(LATEST_JSON_PATH, payload)

    worker_state.setdefault("lastDigests", {})[payload["windowId"]] = {
        "windowId": payload["windowId"],
        "label": payload["label"],
        "generatedAt": payload["generatedAt"],
        "totalItems": payload["totalItems"],
        "pathMd": str(md_path.relative_to(WORKSPACE_ROOT)),
        "pathJson": str(json_path.relative_to(WORKSPACE_ROOT)),
    }
    update_worker_state(worker_state, mode=f"digest:{payload['windowId']}", now_utc=now_utc)
    write_json(WORKER_STATE_PATH, worker_state)
    sync_managed_worker_state(worker_state)
    return {
        "windowId": payload["windowId"],
        "generatedAt": payload["generatedAt"],
        "items": payload["totalItems"],
        "pathMd": str(md_path.relative_to(WORKSPACE_ROOT)),
        "pathJson": str(json_path.relative_to(WORKSPACE_ROOT)),
    }



def generate_digest(window_id: str, *, force: bool = False) -> dict[str, Any]:
    now_utc = utc_now()
    settings = load_settings()
    worker_state = load_worker_state()
    windows = {window["id"]: window for window in settings.get("digestWindows", [])}
    if window_id not in windows:
        raise SystemExit(f"Unknown digest window: {window_id}")
    payload = build_digest_payload(windows[window_id], settings, worker_state, now_utc)
    if payload is None and not force:
        return {"windowId": window_id, "generated": False, "reason": "threshold-not-met"}
    if payload is None and force:
        payload = {
            "windowId": windows[window_id]["id"],
            "label": windows[window_id]["label"],
            "generatedAt": iso(now_utc),
            "timezone": settings.get("timezone", "America/New_York"),
            "windowStart": iso(now_utc - timedelta(hours=float(windows[window_id].get("lookbackHours", 4)))),
            "windowEnd": iso(now_utc),
            "totalItems": 0,
            "totalScore": 0,
            "highPriorityCount": 0,
            "topCategories": [],
            "unresolvedUncertainties": [],
            "items": [],
        }
    result = write_digest(payload, settings, worker_state, now_utc)
    result["generated"] = True
    return result



def command_collect(args: argparse.Namespace) -> int:
    summary = collect_observations(args)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Collected {summary['newObservations']} new observations ({summary['digestEligible']} digest-eligible, {summary['highPriority']} high-priority).")
        for item in summary["sourceSummaries"]:
            status = item["status"]
            print(f"- {item['label']}: status={status} new={item['acceptedItems']} fetched={item['fetchedItems']}")
            if item.get("error"):
                print(f"  error={item['error']}")
    return 0



def command_digest(args: argparse.Namespace) -> int:
    result = generate_digest(args.window_id, force=args.force)
    user_results: list[dict[str, Any]] = []
    if result.get("generated"):
        user_results = generate_user_digests_for_global(result)
        result["userDigestsGenerated"] = user_results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("generated"):
            print(f"Wrote digest {args.window_id}: {result['pathMd']}")
            if user_results:
                for item in user_results:
                    print(f"user digest {item['userId']} -> {item['pathMd']}")
        else:
            print(f"Skipped digest {args.window_id}: {result['reason']}")
    return 0



def command_status(args: argparse.Namespace) -> int:
    worker_state = load_worker_state()
    source_health = read_json(SOURCE_HEALTH_PATH, {})
    latest = read_json(LATEST_JSON_PATH, None)
    payload = {
        "workerState": worker_state,
        "latestDigest": latest,
        "sourceHealth": source_health,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(f"Last run: {worker_state.get('lastRunAt')} ({worker_state.get('lastRunMode')})")
    print(f"Last collect: {worker_state.get('lastCollectAt')}")
    print(f"Observations stored: {worker_state.get('observationCount', 0)}")
    last_digests = worker_state.get("lastDigests", {}) or {}
    if last_digests:
        print("Digests:")
        for key in sorted(last_digests):
            item = last_digests[key]
            print(f"- {key}: {item.get('generatedAt')} ({item.get('totalItems')} items) -> {item.get('pathMd')}")
    else:
        print("Digests: none yet")
    last_user_digests = worker_state.get("lastUserDigests", {}) or {}
    if last_user_digests:
        print("User digests:")
        for window_id in sorted(last_user_digests):
            for user_id, item in sorted((last_user_digests.get(window_id) or {}).items()):
                print(f"- {window_id}/{user_id}: {item.get('generatedAt')} ({item.get('matchedItemCount')} matches) -> {item.get('pathMd')}")
    print("Sources:")
    for source_id, info in sorted(source_health.items()):
        print(f"- {source_id}: status={info.get('status')} fetchedAt={info.get('fetchedAt')} items={info.get('fetchedItems')} error={info.get('error')}")
    return 0



def cron_block() -> str:
    python_path = sys.executable or "/usr/bin/python3"
    return "\n".join(
        [
            CRON_BEGIN,
            "CRON_TZ=America/New_York",
            f"*/20 6-18 * * 1-5 cd {WORKSPACE_ROOT} && {python_path} {SKILL_ROOT / 'scripts' / 'market_digest.py'} scheduled-run >> {CRON_LOG_PATH} 2>&1",
            CRON_END,
        ]
    )



def command_print_crontab(_args: argparse.Namespace) -> int:
    print(cron_block())
    return 0



def install_crontab() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    current = ""
    proc = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if proc.returncode == 0:
        current = proc.stdout.strip()
    elif proc.returncode != 1:
        raise SystemExit(proc.stderr.strip() or "Failed to read current crontab")

    pattern = re.compile(re.escape(CRON_BEGIN) + r".*?" + re.escape(CRON_END), re.S)
    block = cron_block()
    if pattern.search(current):
        updated = pattern.sub(block, current).strip()
    else:
        updated = (current + "\n\n" + block).strip() if current else block

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as fh:
        fh.write(updated)
        fh.write("\n")
        temp_path = fh.name
    try:
        apply_proc = subprocess.run(["crontab", temp_path], capture_output=True, text=True)
        if apply_proc.returncode != 0:
            raise SystemExit(apply_proc.stderr.strip() or "Failed to install crontab")
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass



def remove_crontab_block() -> None:
    proc = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if proc.returncode not in {0, 1}:
        raise SystemExit(proc.stderr.strip() or "Failed to read current crontab")
    current = proc.stdout.strip() if proc.returncode == 0 else ""
    pattern = re.compile(re.escape(CRON_BEGIN) + r".*?" + re.escape(CRON_END), re.S)
    updated = pattern.sub("", current).strip()
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as fh:
        fh.write(updated + ("\n" if updated else ""))
        temp_path = fh.name
    try:
        apply_proc = subprocess.run(["crontab", temp_path], capture_output=True, text=True)
        if apply_proc.returncode != 0:
            raise SystemExit(apply_proc.stderr.strip() or "Failed to update crontab")
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass



def command_install_crontab(_args: argparse.Namespace) -> int:
    install_crontab()
    worker_state = load_worker_state()
    worker_state["installedCron"] = True
    update_worker_state(worker_state, mode="install-crontab", now_utc=utc_now())
    write_json(WORKER_STATE_PATH, worker_state)
    sync_managed_worker_state(worker_state)
    print("Installed market digest crontab block.")
    return 0



def command_remove_crontab(_args: argparse.Namespace) -> int:
    remove_crontab_block()
    worker_state = load_worker_state()
    worker_state["installedCron"] = False
    update_worker_state(worker_state, mode="remove-crontab", now_utc=utc_now())
    write_json(WORKER_STATE_PATH, worker_state)
    sync_managed_worker_state(worker_state)
    print("Removed market digest crontab block.")
    return 0



def command_scheduled_run(args: argparse.Namespace) -> int:
    now_utc = utc_now()
    collect_summary = collect_observations(args)
    settings = load_settings()
    worker_state = load_worker_state()
    due = due_digest_windows(settings, worker_state, now_utc)
    generated: list[dict[str, Any]] = []
    user_generated: list[dict[str, Any]] = []
    for window in due:
        result = generate_digest(window["id"], force=False)
        if result.get("generated"):
            generated.append(result)
            user_generated.extend(generate_user_digests_for_global(result))
    payload = {
        "ranAt": iso(now_utc),
        "collect": collect_summary,
        "digestsGenerated": generated,
        "userDigestsGenerated": user_generated,
        "dueWindows": [window["id"] for window in due],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"scheduled-run @ {payload['ranAt']} | new={collect_summary['newObservations']} eligible={collect_summary['digestEligible']} high={collect_summary['highPriority']}")
        if generated:
            for item in generated:
                print(f"digest {item['windowId']} -> {item['pathMd']}")
            for item in user_generated:
                print(f"user digest {item['userId']} -> {item['pathMd']}")
        else:
            print("no digest emitted")
    return 0



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    collect = sub.add_parser("collect", help="Fetch feeds and store new observations")
    collect.add_argument("--json", action="store_true")
    collect.set_defaults(func=command_collect)

    digest = sub.add_parser("digest", help="Compile one digest window")
    digest.add_argument("window_id", choices=["morning", "midday", "close"])
    digest.add_argument("--force", action="store_true")
    digest.add_argument("--json", action="store_true")
    digest.set_defaults(func=command_digest)

    scheduled = sub.add_parser("scheduled-run", help="Collect, then emit due digests if thresholds are met")
    scheduled.add_argument("--json", action="store_true")
    scheduled.set_defaults(func=command_scheduled_run)

    status = sub.add_parser("status", help="Show worker/source/digest status")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=command_status)

    print_cron = sub.add_parser("print-crontab", help="Print the recommended crontab block")
    print_cron.set_defaults(func=command_print_crontab)

    install = sub.add_parser("install-crontab", help="Install/update the market digest crontab block")
    install.set_defaults(func=command_install_crontab)

    remove = sub.add_parser("remove-crontab", help="Remove the market digest crontab block")
    remove.set_defaults(func=command_remove_crontab)

    return parser



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())

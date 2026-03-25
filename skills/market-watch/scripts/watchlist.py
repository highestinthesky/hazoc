#!/usr/bin/env python3
"""Workspace-local watchlist with simple price target / stop checks."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yfinance as yf
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: yfinance. Install with: pip install yfinance") from exc

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / 'state'
STATE_DIR.mkdir(parents=True, exist_ok=True)
WATCHLIST_PATH = STATE_DIR / 'watchlist.json'


def load_watchlist() -> list[dict[str, Any]]:
    if not WATCHLIST_PATH.exists():
        return []
    return json.loads(WATCHLIST_PATH.read_text())


def save_watchlist(items: list[dict[str, Any]]) -> None:
    WATCHLIST_PATH.write_text(json.dumps(items, indent=2) + '\n')


def get_price(ticker: str) -> float:
    hist = yf.Ticker(ticker).history(period='5d')
    if hist.empty:
        raise ValueError(f'No recent data for {ticker}')
    return round(float(hist['Close'].dropna().tolist()[-1]), 4)


def cmd_add(args: argparse.Namespace) -> None:
    items = load_watchlist()
    ticker = args.ticker.upper()
    for item in items:
        if item['ticker'] == ticker:
            raise SystemExit(f'{ticker} is already in the watchlist')
    items.append({
        'ticker': ticker,
        'target': args.target,
        'stop': args.stop,
        'note': args.note or '',
        'createdAt': datetime.now(timezone.utc).isoformat(),
    })
    save_watchlist(items)
    print(f'Added {ticker}')


def cmd_remove(args: argparse.Namespace) -> None:
    ticker = args.ticker.upper()
    items = [item for item in load_watchlist() if item['ticker'] != ticker]
    save_watchlist(items)
    print(f'Removed {ticker}')


def cmd_list(_args: argparse.Namespace) -> None:
    items = load_watchlist()
    if not items:
        print('Watchlist is empty')
        return
    for item in items:
        print(json.dumps(item, ensure_ascii=False))


def cmd_check(args: argparse.Namespace) -> None:
    out = []
    for item in load_watchlist():
        ticker = item['ticker']
        price = get_price(ticker)
        flags = []
        if item.get('target') is not None and price >= float(item['target']):
            flags.append('target_hit')
        if item.get('stop') is not None and price <= float(item['stop']):
            flags.append('stop_hit')
        out.append({**item, 'price': price, 'flags': flags, 'checkedAt': datetime.now(timezone.utc).isoformat()})
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for item in out:
            flag_text = ', '.join(item['flags']) if item['flags'] else 'none'
            print(f"{item['ticker']}: {item['price']} | flags={flag_text} | note={item.get('note','')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Workspace-local watchlist')
    sub = parser.add_subparsers(dest='command', required=True)

    add = sub.add_parser('add')
    add.add_argument('ticker')
    add.add_argument('--target', type=float)
    add.add_argument('--stop', type=float)
    add.add_argument('--note')
    add.set_defaults(func=cmd_add)

    remove = sub.add_parser('remove')
    remove.add_argument('ticker')
    remove.set_defaults(func=cmd_remove)

    list_cmd = sub.add_parser('list')
    list_cmd.set_defaults(func=cmd_list)

    check = sub.add_parser('check')
    check.add_argument('--json', action='store_true')
    check.set_defaults(func=cmd_check)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

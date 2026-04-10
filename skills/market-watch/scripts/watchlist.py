#!/usr/bin/env python3
"""Workspace-local multi-user watchlist with simple target / stop checks."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / 'config'
STATE_DIR = ROOT / 'state'
STATE_DIR.mkdir(parents=True, exist_ok=True)
WATCHLIST_PATH = STATE_DIR / 'watchlist.json'
USERS_PATH = CONFIG_DIR / 'digest_users.json'


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())



def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n')



def load_users() -> list[dict[str, Any]]:
    payload = read_json(USERS_PATH, {"users": []})
    return [user for user in payload.get('users', []) if user.get('enabled', True)]



def known_user_ids() -> set[str]:
    return {str(user['userId']) for user in load_users() if user.get('userId')}



def sole_user_id() -> str | None:
    ids = sorted(known_user_ids())
    return ids[0] if len(ids) == 1 else None



def normalize_user_id(user_id: str | None) -> str:
    if user_id:
        return user_id.strip()
    return sole_user_id() or 'default'



def require_known_user(user_id: str) -> None:
    ids = known_user_ids()
    if ids and user_id not in ids:
        raise SystemExit(f'Unknown user: {user_id}. Known users: {", ".join(sorted(ids))}')



def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(item)
    normalized['ticker'] = str(normalized['ticker']).upper()
    normalized['userId'] = normalize_user_id(normalized.get('userId'))
    normalized.setdefault('note', '')
    normalized.setdefault('aliases', [])
    normalized.setdefault('importance', 'normal')
    return normalized



def load_watchlist() -> list[dict[str, Any]]:
    items = read_json(WATCHLIST_PATH, [])
    return [normalize_item(item) for item in items]



def save_watchlist(items: list[dict[str, Any]]) -> None:
    normalized = [normalize_item(item) for item in items]
    normalized.sort(key=lambda item: (item.get('userId', ''), item['ticker']))
    write_json(WATCHLIST_PATH, normalized)



def extract_prices_from_download(history: Any, tickers: list[str]) -> dict[str, float]:
    prices: dict[str, float] = {}
    if history is None or getattr(history, 'empty', True):
        return prices

    if len(tickers) == 1:
        ticker = tickers[0]
        try:
            close_series = history['Close'].dropna()
            if not close_series.empty:
                prices[ticker] = round(float(close_series.iloc[-1]), 4)
        except Exception:
            return prices
        return prices

    for ticker in tickers:
        try:
            close_series = history[ticker]['Close'].dropna()
            if not close_series.empty:
                prices[ticker] = round(float(close_series.iloc[-1]), 4)
        except Exception:
            continue
    return prices



def fetch_price_from_yahoo_chart(ticker: str) -> float | None:
    try:
        import requests
    except ImportError:
        return None

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    try:
        response = requests.get(
            url,
            params={"range": "5d", "interval": "1d", "includePrePost": "false"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    result = (((payload.get('chart') or {}).get('result') or [None])[0] or {})
    meta = result.get('meta') or {}
    for key in ('regularMarketPrice', 'previousClose', 'chartPreviousClose'):
        value = meta.get(key)
        if isinstance(value, (int, float)):
            return round(float(value), 4)

    closes = ((((result.get('indicators') or {}).get('quote') or [{}])[0]).get('close') or [])
    numeric_closes = [value for value in closes if isinstance(value, (int, float))]
    if numeric_closes:
        return round(float(numeric_closes[-1]), 4)
    return None



def get_prices(tickers: list[str]) -> dict[str, float]:
    unique = sorted({ticker.upper() for ticker in tickers})
    if not unique:
        return {}

    prices: dict[str, float] = {}
    yf = None
    try:
        import yfinance as yf  # type: ignore
    except ImportError:
        yf = None

    if yf is not None:
        try:
            history = yf.download(
                tickers=unique,
                period='5d',
                auto_adjust=False,
                progress=False,
                threads=True,
                group_by='ticker',
            )
            prices.update(extract_prices_from_download(history, unique))
        except Exception:
            pass

        missing = [ticker for ticker in unique if ticker not in prices]
        for ticker in missing:
            try:
                hist = yf.Ticker(ticker).history(period='5d')
                if hist.empty:
                    continue
                prices[ticker] = round(float(hist['Close'].dropna().tolist()[-1]), 4)
            except Exception:
                continue

    missing = [ticker for ticker in unique if ticker not in prices]
    for ticker in missing:
        price = fetch_price_from_yahoo_chart(ticker)
        if price is not None:
            prices[ticker] = price

    return prices



def choose_user(args: argparse.Namespace, *, required: bool) -> str | None:
    if getattr(args, 'user', None):
        user_id = normalize_user_id(args.user)
        require_known_user(user_id)
        return user_id
    if required:
        user_id = normalize_user_id(None)
        require_known_user(user_id)
        return user_id
    if sole_user_id():
        return sole_user_id()
    return None



def cmd_add(args: argparse.Namespace) -> None:
    items = load_watchlist()
    ticker = args.ticker.upper()
    user_id = choose_user(args, required=True)
    assert user_id is not None

    for item in items:
        if item['ticker'] == ticker and item.get('userId') == user_id:
            raise SystemExit(f'{ticker} is already in the watchlist for {user_id}')

    aliases = [alias.strip() for alias in (args.alias or []) if alias.strip()]
    items.append({
        'userId': user_id,
        'ticker': ticker,
        'target': args.target,
        'stop': args.stop,
        'note': args.note or '',
        'aliases': aliases,
        'importance': args.importance,
        'createdAt': datetime.now(timezone.utc).isoformat(),
    })
    save_watchlist(items)
    print(f'Added {ticker} for {user_id}')



def cmd_remove(args: argparse.Namespace) -> None:
    ticker = args.ticker.upper()
    items = load_watchlist()
    chosen_user = choose_user(args, required=False)

    if chosen_user is None:
        matches = [item for item in items if item['ticker'] == ticker]
        owners = sorted({item['userId'] for item in matches})
        if len(owners) > 1:
            raise SystemExit(f'{ticker} belongs to multiple users ({", ".join(owners)}). Re-run with --user.')
        chosen_user = owners[0] if owners else None

    filtered = [item for item in items if not (item['ticker'] == ticker and (chosen_user is None or item['userId'] == chosen_user))]
    if len(filtered) == len(items):
        if chosen_user:
            raise SystemExit(f'{ticker} is not in the watchlist for {chosen_user}')
        raise SystemExit(f'{ticker} is not in the watchlist')
    save_watchlist(filtered)
    if chosen_user:
        print(f'Removed {ticker} for {chosen_user}')
    else:
        print(f'Removed {ticker}')



def filtered_items(args: argparse.Namespace) -> list[dict[str, Any]]:
    items = load_watchlist()
    chosen_user = choose_user(args, required=False)
    if chosen_user:
        return [item for item in items if item.get('userId') == chosen_user]
    return items



def cmd_list(args: argparse.Namespace) -> None:
    items = filtered_items(args)
    if not items:
        print('Watchlist is empty')
        return
    if args.json:
        print(json.dumps(items, indent=2))
        return
    for item in items:
        print(json.dumps(item, ensure_ascii=False))



def cmd_check(args: argparse.Namespace) -> None:
    items = filtered_items(args)
    prices = get_prices([item['ticker'] for item in items])
    checked_at = datetime.now(timezone.utc).isoformat()
    out = []
    for item in items:
        ticker = item['ticker']
        price = prices.get(ticker)
        flags = []
        if price is None:
            flags.append('price_unavailable')
        else:
            if item.get('target') is not None and price >= float(item['target']):
                flags.append('target_hit')
            if item.get('stop') is not None and price <= float(item['stop']):
                flags.append('stop_hit')
        out.append({**item, 'price': price, 'flags': flags, 'checkedAt': checked_at})
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for item in out:
            flag_text = ', '.join(item['flags']) if item['flags'] else 'none'
            print(
                f"{item['userId']} | {item['ticker']}: {item['price']} | flags={flag_text} | note={item.get('note', '')}"
            )



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Workspace-local multi-user watchlist')
    sub = parser.add_subparsers(dest='command', required=True)

    add = sub.add_parser('add')
    add.add_argument('ticker')
    add.add_argument('--user')
    add.add_argument('--target', type=float)
    add.add_argument('--stop', type=float)
    add.add_argument('--note')
    add.add_argument('--alias', action='append', default=[])
    add.add_argument('--importance', choices=['low', 'normal', 'high', 'core'], default='normal')
    add.set_defaults(func=cmd_add)

    remove = sub.add_parser('remove')
    remove.add_argument('ticker')
    remove.add_argument('--user')
    remove.set_defaults(func=cmd_remove)

    list_cmd = sub.add_parser('list')
    list_cmd.add_argument('--user')
    list_cmd.add_argument('--json', action='store_true')
    list_cmd.set_defaults(func=cmd_list)

    check = sub.add_parser('check')
    check.add_argument('--user')
    check.add_argument('--json', action='store_true')
    check.set_defaults(func=cmd_check)

    return parser



def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

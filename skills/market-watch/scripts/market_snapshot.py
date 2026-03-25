#!/usr/bin/env python3
"""Compact stock/crypto snapshot tool using public Yahoo Finance data."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from statistics import mean
from typing import Any

try:
    import yfinance as yf
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: yfinance. Install with: pip install yfinance") from exc


def pct_change(new: float | None, old: float | None) -> float | None:
    if new in (None, 0) or old in (None, 0):
        return None
    try:
        return round(((new - old) / old) * 100, 2)
    except ZeroDivisionError:
        return None


def clean_number(value: Any) -> float | int | None:
    if value is None:
        return None
    try:
        if isinstance(value, bool):
            return None
        num = float(value)
        if math.isnan(num) or math.isinf(num):
            return None
        if num.is_integer():
            return int(num)
        return round(num, 4)
    except Exception:
        return None


def sma(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return round(mean(values[-window:]), 4)


def rsi14(values: list[float]) -> float | None:
    if len(values) < 15:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, 15):
        delta = values[-15 + i] - values[-15 + i - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))
    avg_gain = mean(gains)
    avg_loss = mean(losses)
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def analyze_ticker(ticker: str, period: str) -> dict[str, Any]:
    t = yf.Ticker(ticker)
    info = t.info or {}
    hist = t.history(period=period, auto_adjust=False)
    if hist.empty:
        raise ValueError(f"No price history returned for {ticker}")

    closes = [float(x) for x in hist["Close"].dropna().tolist()]
    latest = closes[-1]
    prev = closes[-2] if len(closes) >= 2 else None
    five_back = closes[-6] if len(closes) >= 6 else None
    month_back = closes[-22] if len(closes) >= 22 else None

    low_52w = clean_number(info.get("fiftyTwoWeekLow"))
    high_52w = clean_number(info.get("fiftyTwoWeekHigh"))
    range_position = None
    if isinstance(low_52w, (int, float)) and isinstance(high_52w, (int, float)) and high_52w > low_52w:
        range_position = round(((latest - low_52w) / (high_52w - low_52w)) * 100, 2)

    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50)
    rsi = rsi14(closes)

    asset_type = "crypto" if ticker.upper().endswith("-USD") else "stock"
    dividend_yield = info.get("dividendYield")
    if dividend_yield is not None:
        dividend_yield = round(float(dividend_yield) * 100, 2)

    signals: list[str] = []
    if sma20 and latest > sma20:
        signals.append("above_sma20")
    if sma50 and latest > sma50:
        signals.append("above_sma50")
    if rsi is not None:
        if rsi >= 70:
            signals.append("rsi_overbought")
        elif rsi <= 30:
            signals.append("rsi_oversold")
    if range_position is not None:
        if range_position >= 85:
            signals.append("near_52w_high")
        elif range_position <= 15:
            signals.append("near_52w_low")

    return {
        "ticker": ticker.upper(),
        "assetType": asset_type,
        "name": info.get("shortName") or info.get("longName") or ticker.upper(),
        "currency": info.get("currency") or "USD",
        "price": round(latest, 4),
        "change1dPct": pct_change(latest, prev),
        "change5dPct": pct_change(latest, five_back),
        "change1mPct": pct_change(latest, month_back),
        "marketCap": clean_number(info.get("marketCap")),
        "trailingPE": clean_number(info.get("trailingPE")),
        "forwardPE": clean_number(info.get("forwardPE")),
        "dividendYieldPct": dividend_yield,
        "fiftyTwoWeekLow": low_52w,
        "fiftyTwoWeekHigh": high_52w,
        "rangePositionPct": range_position,
        "sma20": sma20,
        "sma50": sma50,
        "rsi14": rsi,
        "signals": signals,
        "asOf": datetime.now(timezone.utc).isoformat(),
      }


def print_text(results: list[dict[str, Any]]) -> None:
    for item in results:
        print(f"\n=== {item['ticker']} · {item['name']} ===")
        print(f"Type: {item['assetType']} | Price: {item['price']} {item['currency']}")
        print(
            f"1d: {item['change1dPct']}% | 5d: {item['change5dPct']}% | 1m: {item['change1mPct']}%"
        )
        print(
            f"SMA20: {item['sma20']} | SMA50: {item['sma50']} | RSI14: {item['rsi14']}"
        )
        print(
            f"52w low/high: {item['fiftyTwoWeekLow']} / {item['fiftyTwoWeekHigh']} | Range pos: {item['rangePositionPct']}%"
        )
        if item.get("dividendYieldPct") is not None:
            print(f"Dividend yield: {item['dividendYieldPct']}%")
        if item.get("trailingPE") is not None or item.get("forwardPE") is not None:
            print(f"Trailing PE: {item['trailingPE']} | Forward PE: {item['forwardPE']}")
        print("Signals:", ", ".join(item["signals"]) if item["signals"] else "none")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compact market snapshot")
    parser.add_argument("tickers", nargs="+", help="Ticker symbols, e.g. AAPL or BTC-USD")
    parser.add_argument("--period", default="6mo", help="History period for trend context (default: 6mo)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    results = []
    for ticker in args.tickers:
        try:
            results.append(analyze_ticker(ticker, args.period))
        except Exception as exc:
            results.append({"ticker": ticker.upper(), "error": str(exc)})

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_text(results)


if __name__ == "__main__":
    main()

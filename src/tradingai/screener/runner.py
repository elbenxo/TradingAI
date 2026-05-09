"""Run the pattern matcher across a universe of symbols."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from tradingai.screener.pattern_matcher import (
    PatternMatch,
    PostSpikeAccumulationPattern,
)

_USER_AGENT = "Mozilla/5.0"
_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


def load_universe(path: str | Path) -> List[str]:
    """Read a newline-separated list of tickers (lines starting with # ignored)."""
    p = Path(path)
    out: list[str] = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line.split()[0].upper())
    # Deduplicate but preserve order
    seen: set[str] = set()
    deduped: list[str] = []
    for s in out:
        if s not in seen:
            deduped.append(s)
            seen.add(s)
    return deduped


def _fetch_weekly(symbol: str, weeks: int = 90) -> pd.DataFrame:
    end = datetime.utcnow()
    start = end - timedelta(weeks=weeks + 4)
    params = {
        "period1": int(start.timestamp()),
        "period2": int(end.timestamp()),
        "interval": "1wk",
    }
    url = _CHART_URL.format(symbol=symbol) + "?" + urlencode(params)
    try:
        req = Request(url, headers={"User-Agent": _USER_AGENT})
        with urlopen(req, timeout=10) as resp:
            payload = json.load(resp)
    except Exception:
        return pd.DataFrame()

    result = (payload.get("chart") or {}).get("result")
    if not result:
        return pd.DataFrame()
    res = result[0]
    ts = res.get("timestamp") or []
    quote = (res.get("indicators") or {}).get("quote", [{}])[0]
    rows = []
    for i, t in enumerate(ts):
        o = quote.get("open", [None] * len(ts))[i]
        h = quote.get("high", [None] * len(ts))[i]
        lo = quote.get("low", [None] * len(ts))[i]
        c = quote.get("close", [None] * len(ts))[i]
        v = quote.get("volume", [None] * len(ts))[i]
        if None in (o, h, lo, c):
            continue
        rows.append({
            "date": datetime.utcfromtimestamp(t),
            "open": o, "high": h, "low": lo, "close": c, "volume": v or 0,
        })
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).set_index("date")
    return df[["open", "high", "low", "close", "volume"]]


def screen(
    symbols: Iterable[str],
    pattern: PostSpikeAccumulationPattern | None = None,
    weeks: int = 90,
    workers: int = 8,
    progress: bool = False,
) -> List[PatternMatch]:
    """Score every symbol in `symbols` and return their PatternMatch results."""
    pattern = pattern or PostSpikeAccumulationPattern()
    results: list[PatternMatch] = []
    symbols = list(symbols)

    def work(sym: str) -> PatternMatch:
        df = _fetch_weekly(sym, weeks=weeks)
        return pattern.evaluate(sym, df)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(work, s): s for s in symbols}
        for i, fut in enumerate(as_completed(futures), 1):
            sym = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                res = PatternMatch(sym, False, 0.0, 0.0, notes=[f"error: {e}"])
            results.append(res)
            if progress and i % 25 == 0:
                print(f"  scanned {i}/{len(symbols)}")
    return results


def to_dataframe(results: list[PatternMatch]) -> pd.DataFrame:
    return pd.DataFrame([r.as_row() for r in results])

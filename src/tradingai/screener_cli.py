"""CLI for the post-spike accumulation pattern screener.

Examples
--------

# Use the bundled penny/small-cap universe
python -m tradingai.screener_cli --universe data/universes/small_caps.txt

# Score a custom list of tickers
python -m tradingai.screener_cli --tickers AAPL TSLA NVDA

# Lower the threshold and surface near-matches
python -m tradingai.screener_cli --universe data/universes/small_caps.txt \
    --min-score 0.4 --top 30
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from tradingai.screener.pattern_matcher import PostSpikeAccumulationPattern
from tradingai.screener.runner import load_universe, screen, to_dataframe


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--universe", type=Path, help="Path to a ticker list file")
    src.add_argument("--tickers", nargs="+", help="Inline list of tickers")

    p.add_argument("--weeks", type=int, default=90, help="Weeks of history to fetch")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--top", type=int, default=20, help="How many results to show")
    p.add_argument("--min-score", type=float, default=0.5)
    p.add_argument("--max-price", type=float, default=10.0,
                   help="Skip stocks with last close above this price")
    p.add_argument("--spike-min-ratio", type=float, default=2.5)
    p.add_argument("--consolidation-weeks", type=int, default=4)
    p.add_argument("--no-require-breakout", action="store_true",
                   help="Don't require a breakout candle on the last bar")
    p.add_argument("--csv", type=Path, default=None,
                   help="Optional: write full ranked results to this CSV")
    p.add_argument("--progress", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.universe:
        symbols = load_universe(args.universe)
        print(f"Loaded {len(symbols)} symbols from {args.universe}")
    else:
        symbols = [s.upper() for s in args.tickers]
        print(f"Scanning {len(symbols)} inline tickers")

    pattern = PostSpikeAccumulationPattern(
        spike_min_ratio=args.spike_min_ratio,
        consolidation_weeks=args.consolidation_weeks,
        max_last_close=args.max_price,
        require_breakout=not args.no_require_breakout,
    )

    results = screen(
        symbols,
        pattern=pattern,
        weeks=args.weeks,
        workers=args.workers,
        progress=args.progress,
    )

    df = to_dataframe(results).sort_values("score", ascending=False)

    if args.csv:
        df.to_csv(args.csv, index=False)
        print(f"Wrote full results to {args.csv}")

    matches = df[df["score"] >= args.min_score].head(args.top)
    print()
    if matches.empty:
        print(f"No symbols scored >= {args.min_score}")
        print("Top 10 by score (all below threshold):")
        print(df.head(10).to_string(index=False))
    else:
        print(f"Top {len(matches)} matches (score >= {args.min_score}):")
        print(matches.to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())

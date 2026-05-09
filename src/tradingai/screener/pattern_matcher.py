"""Post-spike accumulation pattern matcher.

The pattern this module looks for is the one described in the screenshot:

  1. ~10-14 weekly candles ago there was a SPIKE: a single weekly candle
     with a range many multiples larger than its surroundings.
  2. After the spike, price entered a long DOWNTREND that gradually faded.
  3. The most recent ~4 weekly candles show flat / tight CONSOLIDATION
     (each weekly range is small relative to price).
  4. Volume during the consolidation phase is meaningfully LOWER than
     during the spike phase (i.e. accumulation, not distribution).
  5. The most recent weekly candle is GREEN with a strong push higher,
     ideally on a Friday breakout into the consolidation high.

Each rule contributes to a 0..1 confidence score. Stocks above a
configurable threshold are reported as matches.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class PatternMatch:
    """Result of running the pattern matcher on a single symbol."""

    symbol: str
    matched: bool
    score: float
    last_close: float
    spike_week_ago: Optional[int] = None
    spike_ratio: Optional[float] = None
    decline_pct: Optional[float] = None
    consolidation_range_pct: Optional[float] = None
    volume_drop_ratio: Optional[float] = None
    last_candle_change_pct: Optional[float] = None
    notes: list = field(default_factory=list)

    def as_row(self) -> dict:
        return {
            "symbol": self.symbol,
            "score": round(self.score, 3),
            "last_close": round(self.last_close, 4) if self.last_close else None,
            "spike_week_ago": self.spike_week_ago,
            "spike_ratio": round(self.spike_ratio, 2) if self.spike_ratio else None,
            "decline_pct": round(self.decline_pct, 1) if self.decline_pct else None,
            "consol_range_pct": (
                round(self.consolidation_range_pct, 2)
                if self.consolidation_range_pct is not None
                else None
            ),
            "vol_drop_ratio": (
                round(self.volume_drop_ratio, 2)
                if self.volume_drop_ratio is not None
                else None
            ),
            "last_change_pct": (
                round(self.last_candle_change_pct, 2)
                if self.last_candle_change_pct is not None
                else None
            ),
            "notes": "; ".join(self.notes),
        }


class PostSpikeAccumulationPattern:
    """Detects the post-spike consolidation/accumulation breakout pattern."""

    def __init__(
        self,
        spike_lookback_weeks: tuple[int, int] = (8, 16),
        spike_min_ratio: float = 2.5,
        consolidation_weeks: int = 4,
        consolidation_max_range_pct: float = 0.25,
        min_decline_from_spike: float = 0.40,
        min_volume_drop_ratio: float = 0.40,
        min_breakout_change_pct: float = 0.10,
        max_last_close: Optional[float] = None,
        require_breakout: bool = True,
    ):
        self.spike_lookback_weeks = spike_lookback_weeks
        self.spike_min_ratio = spike_min_ratio
        self.consolidation_weeks = consolidation_weeks
        self.consolidation_max_range_pct = consolidation_max_range_pct
        self.min_decline_from_spike = min_decline_from_spike
        self.min_volume_drop_ratio = min_volume_drop_ratio
        self.min_breakout_change_pct = min_breakout_change_pct
        self.max_last_close = max_last_close
        self.require_breakout = require_breakout

    def evaluate(self, symbol: str, weekly: pd.DataFrame) -> PatternMatch:
        """Score one weekly OHLCV dataframe against the pattern."""
        notes: list[str] = []

        if weekly is None or weekly.empty:
            return PatternMatch(symbol, False, 0.0, 0.0, notes=["empty data"])

        df = weekly.dropna(subset=["open", "high", "low", "close"]).copy()
        min_bars = max(self.spike_lookback_weeks) + self.consolidation_weeks + 2
        if len(df) < min_bars:
            return PatternMatch(
                symbol, False, 0.0,
                float(df["close"].iloc[-1]) if not df.empty else 0.0,
                notes=[f"need {min_bars} weekly bars, have {len(df)}"],
            )

        last_close = float(df["close"].iloc[-1])
        if self.max_last_close is not None and last_close > self.max_last_close:
            return PatternMatch(
                symbol, False, 0.0, last_close,
                notes=[f"price {last_close:.2f} above {self.max_last_close}"],
            )

        score = 0.0
        weights = {
            "spike": 0.25,
            "decline": 0.20,
            "consolidation": 0.20,
            "volume": 0.15,
            "breakout": 0.20,
        }

        # ---- 1) Spike detection ----
        spike_lo, spike_hi = self.spike_lookback_weeks
        # weeks_ago counts back from the most recent candle (1 = previous week)
        spike_idx = None
        spike_ratio = 0.0
        spike_high = 0.0
        for weeks_ago in range(spike_lo, spike_hi + 1):
            idx = len(df) - 1 - weeks_ago
            if idx < 4:
                continue
            row = df.iloc[idx]
            window = df.iloc[max(0, idx - 4): idx]
            if window.empty or window["close"].mean() <= 0:
                continue
            ratio = row["high"] / window["close"].mean()
            if ratio > spike_ratio:
                spike_ratio = ratio
                spike_idx = idx
                spike_high = float(row["high"])

        spike_weeks_ago = (len(df) - 1 - spike_idx) if spike_idx is not None else None
        if spike_ratio >= self.spike_min_ratio:
            score += weights["spike"]
            notes.append(f"spike x{spike_ratio:.1f} {spike_weeks_ago}w ago")
        else:
            notes.append(f"weak spike x{spike_ratio:.1f}")

        # ---- 2) Decline from spike high ----
        decline_pct = None
        if spike_idx is not None and spike_high > 0:
            consol_window = df.iloc[-(self.consolidation_weeks + 1): -1]
            if not consol_window.empty:
                consol_close = float(consol_window["close"].mean())
                decline_pct = (spike_high - consol_close) / spike_high
                if decline_pct >= self.min_decline_from_spike:
                    score += weights["decline"]
                    notes.append(f"decline {decline_pct:.0%} from spike")

        # ---- 3) Flat consolidation in last N weeks (excluding the latest) ----
        consol = df.iloc[-(self.consolidation_weeks + 1): -1]
        consolidation_range_pct = None
        if not consol.empty:
            ranges_pct = (consol["high"] - consol["low"]) / consol["close"]
            consolidation_range_pct = float(ranges_pct.mean())
            std_close = float(consol["close"].std() / consol["close"].mean())
            if (
                consolidation_range_pct <= self.consolidation_max_range_pct
                and std_close <= self.consolidation_max_range_pct
            ):
                score += weights["consolidation"]
                notes.append(
                    f"flat consol range {consolidation_range_pct:.0%}"
                )

        # ---- 4) Volume drop (consolidation vs spike) ----
        volume_drop_ratio = None
        if "volume" in df.columns and spike_idx is not None:
            spike_vol = float(df.iloc[spike_idx]["volume"])
            consol_vol = float(consol["volume"].mean()) if not consol.empty else 0.0
            if spike_vol > 0:
                # We want consolidation vol to be a fraction of spike vol.
                # volume_drop_ratio = 1 - consol/spike.
                volume_drop_ratio = 1.0 - (consol_vol / spike_vol)
                if volume_drop_ratio >= self.min_volume_drop_ratio:
                    score += weights["volume"]
                    notes.append(f"vol drop {volume_drop_ratio:.0%}")

        # ---- 5) Recent breakout candle ----
        last = df.iloc[-1]
        prev = df.iloc[-2]
        last_change_pct = float((last["close"] - prev["close"]) / prev["close"])
        is_green = last["close"] > last["open"]
        if is_green and last_change_pct >= self.min_breakout_change_pct:
            score += weights["breakout"]
            notes.append(f"breakout +{last_change_pct:.0%}")
        elif self.require_breakout:
            notes.append(f"no breakout (last {last_change_pct:+.1%})")

        matched = (
            score >= 0.55
            and (not self.require_breakout or last_change_pct >= self.min_breakout_change_pct)
            and spike_ratio >= self.spike_min_ratio
        )

        return PatternMatch(
            symbol=symbol,
            matched=matched,
            score=score,
            last_close=last_close,
            spike_week_ago=spike_weeks_ago,
            spike_ratio=spike_ratio,
            decline_pct=decline_pct,
            consolidation_range_pct=consolidation_range_pct,
            volume_drop_ratio=volume_drop_ratio,
            last_candle_change_pct=last_change_pct,
            notes=notes,
        )

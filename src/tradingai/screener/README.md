# Post-spike accumulation screener

Detects the chart pattern shared in the FinanceLancelot screenshot:

1. A massive single-week SPIKE candle ~10–14 months ago.
2. A long DECLINE / fade through several months.
3. ~4 weeks of FLAT consolidation candles.
4. VOLUME during consolidation a small fraction of spike volume (accumulation, not distribution).
5. A recent BREAKOUT candle (Friday rip).

## Usage

```bash
# Run against the bundled US small/penny universe
PYTHONPATH=src python -m tradingai.screener_cli \
    --universe data/universes/small_caps.txt \
    --max-price 5 --min-score 0.55 --top 30

# Tune for the FinanceLancelot June-2025 setup (spike 40-52 weeks ago)
PYTHONPATH=src python -c "
from tradingai.screener.pattern_matcher import PostSpikeAccumulationPattern
from tradingai.screener.runner import load_universe, screen, to_dataframe

p = PostSpikeAccumulationPattern(
    spike_lookback_weeks=(40, 52),
    spike_min_ratio=2.0,
    consolidation_weeks=4,
    min_decline_from_spike=0.30,
    min_volume_drop_ratio=0.50,
    max_last_close=2.0,
    require_breakout=False,
)
syms = load_universe('data/universes/small_caps.txt')
df = to_dataframe(screen(syms, pattern=p, weeks=70))
print(df.sort_values('score', ascending=False).head(30).to_string(index=False))
"
```

## Public API

- `PostSpikeAccumulationPattern.evaluate(symbol, weekly_df) -> PatternMatch`
- `screener.runner.screen(symbols, pattern=...) -> list[PatternMatch]`
- `PatternMatch.as_row()` flattens a result into a dict for CSV/DataFrame export.

The data fetcher uses Yahoo's chart API directly (no `yfinance` rate limits)
so you can scan thousands of tickers in a few minutes.

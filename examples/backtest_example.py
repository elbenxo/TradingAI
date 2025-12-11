"""Example: How to use the backtesting framework."""

from datetime import datetime, timedelta
from tradingai.data.collector import get_collector
from tradingai.models.backtest import Backtester


def simple_backtest():
    """Run a simple backtest on a single symbol."""

    print("=" * 80)
    print("TradingAI Backtesting Example")
    print("=" * 80)

    # 1. Fetch historical data
    symbol = 'AAPL'
    print(f"\n1. Fetching historical data for {symbol}...")

    collector = get_collector('yfinance')
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years

    data = collector.fetch_historical_data(symbol, start_date, end_date)
    print(f"   ✓ Fetched {len(data)} days of data")

    # 2. Initialize backtester
    print(f"\n2. Setting up backtester...")

    backtester = Backtester(
        initial_capital=10000.0,      # Start with $10,000
        position_size_pct=0.1,        # Use 10% of capital per trade
        stop_loss_pct=0.05,           # 5% stop loss
        take_profit_pct=0.10,         # 10% take profit
        min_confidence=0.7,           # Only take signals with 70%+ confidence
        commission=0.001              # 0.1% commission per trade
    )
    print(f"   ✓ Backtester configured")

    # 3. Run backtest
    print(f"\n3. Running backtest on {symbol}...")

    results = backtester.backtest(symbol, data, strategy='all')

    # 4. Display results
    print(f"\n" + "=" * 80)
    print(f"BACKTEST RESULTS")
    print(f"=" * 80)
    print(f"\nSymbol: {results.symbol}")
    print(f"Period: {results.start_date.strftime('%Y-%m-%d')} to {results.end_date.strftime('%Y-%m-%d')}")
    print(f"\nCapital:")
    print(f"  Initial: ${results.initial_capital:,.2f}")
    print(f"  Final:   ${results.final_capital:,.2f}")
    print(f"  P/L:     ${results.final_capital - results.initial_capital:,.2f}")
    print(f"  Return:  {results.total_return:.2f}%")

    print(f"\nTrade Statistics:")
    print(f"  Total Trades:   {results.total_trades}")
    print(f"  Winning Trades: {results.winning_trades}")
    print(f"  Losing Trades:  {results.losing_trades}")
    print(f"  Win Rate:       {results.win_rate:.2f}%")

    print(f"\nPerformance Metrics:")
    print(f"  Average Win:    ${results.avg_win:,.2f}")
    print(f"  Average Loss:   ${results.avg_loss:,.2f}")
    print(f"  Profit Factor:  {results.profit_factor:.2f}")
    print(f"  Max Drawdown:   {results.max_drawdown:.2f}%")

    # 5. Show sample trades
    if results.trades:
        print(f"\nSample Trades (First 5):")
        print(f"  {'Date':<12} {'Type':<6} {'Entry':<10} {'Exit':<10} {'P/L %':<10} {'Signal'}")
        print(f"  {'-' * 75}")

        closed_trades = [t for t in results.trades if not t.is_open][:5]
        for trade in closed_trades:
            print(
                f"  {trade.entry_date.strftime('%Y-%m-%d'):<12} "
                f"{trade.trade_type.upper():<6} "
                f"${trade.entry_price:<9.2f} "
                f"${trade.exit_price:<9.2f} "
                f"{trade.profit_loss_pct:<9.2f}% "
                f"{trade.signal}"
            )

    print(f"\n" + "=" * 80)


def compare_multiple_symbols():
    """Compare backtesting results across multiple symbols."""

    print("\n" + "=" * 80)
    print("Comparing Multiple Symbols")
    print("=" * 80)

    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    results_dict = {}

    # Collect data
    collector = get_collector('yfinance')
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print(f"\nFetching data for {len(symbols)} symbols...")

    for symbol in symbols:
        print(f"  Fetching {symbol}...", end=" ")
        data = collector.fetch_historical_data(symbol, start_date, end_date)

        if not data.empty:
            backtester = Backtester(
                initial_capital=10000.0,
                position_size_pct=0.1,
                stop_loss_pct=0.05,
                take_profit_pct=0.10,
                min_confidence=0.7
            )

            results = backtester.backtest(symbol, data)
            results_dict[symbol] = results
            print(f"✓ ({results.total_trades} trades)")
        else:
            print(f"✗ (no data)")

    # Display comparison
    print(f"\n" + "=" * 80)
    print(f"COMPARISON RESULTS")
    print(f"=" * 80)
    print(
        f"\n{'Symbol':<8} {'Return %':<12} {'Trades':<10} {'Win Rate %':<12} "
        f"{'Profit Factor':<15}"
    )
    print("-" * 80)

    for symbol, results in results_dict.items():
        print(
            f"{symbol:<8} "
            f"{results.total_return:<12.2f} "
            f"{results.total_trades:<10} "
            f"{results.win_rate:<12.2f} "
            f"{results.profit_factor:<15.2f}"
        )

    # Find best performer
    if results_dict:
        best_symbol = max(results_dict.items(), key=lambda x: x[1].total_return)
        print(f"\n{'-' * 80}")
        print(
            f"Best Performer: {best_symbol[0]} "
            f"with {best_symbol[1].total_return:.2f}% return"
        )
        print(f"=" * 80)


def test_different_strategies():
    """Test different strategies on the same symbol."""

    print("\n" + "=" * 80)
    print("Testing Different Strategies")
    print("=" * 80)

    symbol = 'AAPL'
    strategies = ['all', 'rsi', 'macd', 'ma_cross', 'bollinger']

    # Get data
    collector = get_collector('yfinance')
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    print(f"\nFetching data for {symbol}...")
    data = collector.fetch_historical_data(symbol, start_date, end_date)

    if data.empty:
        print("No data available!")
        return

    print(f"✓ Fetched {len(data)} days of data")

    results_dict = {}

    print(f"\nRunning backtests...")

    for strategy in strategies:
        print(f"  Testing '{strategy}' strategy...", end=" ")

        backtester = Backtester(
            initial_capital=10000.0,
            position_size_pct=0.1,
            stop_loss_pct=0.05,
            take_profit_pct=0.10,
            min_confidence=0.7
        )

        results = backtester.backtest(symbol, data, strategy=strategy)
        results_dict[strategy] = results
        print(f"✓ ({results.total_trades} trades, {results.total_return:.2f}% return)")

    # Display comparison
    print(f"\n" + "=" * 80)
    print(f"STRATEGY COMPARISON: {symbol}")
    print(f"=" * 80)
    print(
        f"\n{'Strategy':<15} {'Return %':<12} {'Trades':<10} {'Win Rate %':<12} "
        f"{'Max DD %':<12}"
    )
    print("-" * 80)

    for strategy, results in results_dict.items():
        print(
            f"{strategy.upper():<15} "
            f"{results.total_return:<12.2f} "
            f"{results.total_trades:<10} "
            f"{results.win_rate:<12.2f} "
            f"{results.max_drawdown:<12.2f}"
        )

    # Find best strategy
    best_strategy = max(results_dict.items(), key=lambda x: x[1].total_return)
    print(f"\n{'-' * 80}")
    print(
        f"Best Strategy: {best_strategy[0].upper()} "
        f"with {best_strategy[1].total_return:.2f}% return"
    )
    print(f"=" * 80)


if __name__ == '__main__':
    # Run all examples
    simple_backtest()
    compare_multiple_symbols()
    test_different_strategies()

    print("\n✓ All examples completed!\n")

"""Command-line interface for backtesting trading strategies."""

import argparse
from datetime import datetime, timedelta
from typing import List
from tradingai.data.collector import get_collector
from tradingai.models.backtest import Backtester
from tradingai.utils.config import config
from tradingai.utils.logger import setup_logger


def run_backtest(
    symbol: str,
    days: int = 365,
    initial_capital: float = 10000.0,
    position_size: float = 0.1,
    stop_loss: float = 0.05,
    take_profit: float = 0.10,
    strategy: str = 'all',
    min_confidence: float = 0.7
) -> None:
    """
    Run backtest for a single symbol.

    Args:
        symbol: Trading symbol
        days: Number of days of historical data
        initial_capital: Starting capital
        position_size: Position size as percentage of capital
        stop_loss: Stop loss percentage
        take_profit: Take profit percentage
        strategy: Strategy to test
        min_confidence: Minimum signal confidence
    """
    logger = setup_logger(level=config.log_level)
    logger.info(f"Running backtest for {symbol}")

    # Get data
    collector = get_collector(config.get('data_sources.primary', 'yfinance'))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    logger.info(f"Fetching {days} days of data for {symbol}")
    data = collector.fetch_historical_data(symbol, start_date, end_date)

    if data.empty:
        logger.error(f"No data available for {symbol}")
        return

    # Initialize backtester
    backtester = Backtester(
        initial_capital=initial_capital,
        position_size_pct=position_size,
        stop_loss_pct=stop_loss,
        take_profit_pct=take_profit,
        min_confidence=min_confidence,
        commission=0.001  # 0.1% commission
    )

    # Run backtest
    results = backtester.backtest(symbol, data, strategy=strategy)

    # Display results
    print(f"\n{'='*80}")
    print(f"BACKTEST RESULTS: {symbol}")
    print(f"{'='*80}")
    print(f"Period: {results.start_date.strftime('%Y-%m-%d')} to {results.end_date.strftime('%Y-%m-%d')}")
    print(f"Strategy: {strategy.upper()}")
    print(f"\n{'CAPITAL':.<40} {'VALUE':>15}")
    print(f"{'-'*80}")
    print(f"{'Initial Capital':.<40} ${results.initial_capital:>14,.2f}")
    print(f"{'Final Capital':.<40} ${results.final_capital:>14,.2f}")
    print(f"{'Profit/Loss':.<40} ${results.final_capital - results.initial_capital:>14,.2f}")
    print(f"{'Total Return':.<40} {results.total_return:>14.2f}%")

    print(f"\n{'TRADE STATISTICS':.<40} {'VALUE':>15}")
    print(f"{'-'*80}")
    print(f"{'Total Trades':.<40} {results.total_trades:>15}")
    print(f"{'Winning Trades':.<40} {results.winning_trades:>15}")
    print(f"{'Losing Trades':.<40} {results.losing_trades:>15}")
    print(f"{'Win Rate':.<40} {results.win_rate:>14.2f}%")

    print(f"\n{'PERFORMANCE METRICS':.<40} {'VALUE':>15}")
    print(f"{'-'*80}")
    print(f"{'Average Win':.<40} ${results.avg_win:>14,.2f}")
    print(f"{'Average Loss':.<40} ${results.avg_loss:>14,.2f}")
    print(f"{'Profit Factor':.<40} {results.profit_factor:>15.2f}")
    print(f"{'Max Drawdown':.<40} {results.max_drawdown:>14.2f}%")

    # Show some recent trades
    if results.trades:
        print(f"\n{'RECENT TRADES (Last 10)':.<40}")
        print(f"{'-'*80}")
        print(f"{'Date':<12} {'Type':<6} {'Entry':<10} {'Exit':<10} {'P/L %':<10} {'Signal':<30}")
        print(f"{'-'*80}")

        recent_trades = [t for t in results.trades if not t.is_open][-10:]
        for trade in recent_trades:
            print(
                f"{trade.entry_date.strftime('%Y-%m-%d'):<12} "
                f"{trade.trade_type.upper():<6} "
                f"${trade.entry_price:<9.2f} "
                f"${trade.exit_price:<9.2f} "
                f"{trade.profit_loss_pct:<9.2f}% "
                f"{trade.signal:<30}"
            )

    # Buy and hold comparison
    buy_hold_return = ((data.iloc[-1]['close'] - data.iloc[200]['close']) / data.iloc[200]['close']) * 100
    print(f"\n{'COMPARISON':.<40} {'VALUE':>15}")
    print(f"{'-'*80}")
    print(f"{'Strategy Return':.<40} {results.total_return:>14.2f}%")
    print(f"{'Buy & Hold Return':.<40} {buy_hold_return:>14.2f}%")
    print(f"{'Alpha (vs Buy & Hold)':.<40} {results.total_return - buy_hold_return:>14.2f}%")

    print(f"\n{'='*80}\n")


def compare_strategies(
    symbol: str,
    days: int = 365,
    initial_capital: float = 10000.0
) -> None:
    """
    Compare different strategies for a symbol.

    Args:
        symbol: Trading symbol
        days: Number of days of historical data
        initial_capital: Starting capital
    """
    logger = setup_logger(level=config.log_level)
    logger.info(f"Comparing strategies for {symbol}")

    # Get data
    collector = get_collector(config.get('data_sources.primary', 'yfinance'))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    data = collector.fetch_historical_data(symbol, start_date, end_date)

    if data.empty:
        logger.error(f"No data available for {symbol}")
        return

    strategies = ['all', 'rsi', 'macd', 'ma_cross', 'bollinger']
    results_list = []

    for strategy in strategies:
        backtester = Backtester(
            initial_capital=initial_capital,
            position_size_pct=0.1,
            stop_loss_pct=0.05,
            take_profit_pct=0.10,
            min_confidence=0.7
        )

        results = backtester.backtest(symbol, data, strategy=strategy)
        results_list.append((strategy, results))

    # Display comparison
    print(f"\n{'='*100}")
    print(f"STRATEGY COMPARISON: {symbol}")
    print(f"{'='*100}")
    print(
        f"{'Strategy':<15} {'Return %':<12} {'Trades':<10} {'Win Rate %':<12} "
        f"{'Profit Factor':<15} {'Max DD %':<12}"
    )
    print(f"{'-'*100}")

    for strategy, results in results_list:
        print(
            f"{strategy.upper():<15} "
            f"{results.total_return:<12.2f} "
            f"{results.total_trades:<10} "
            f"{results.win_rate:<12.2f} "
            f"{results.profit_factor:<15.2f} "
            f"{results.max_drawdown:<12.2f}"
        )

    # Find best strategy
    best_strategy = max(results_list, key=lambda x: x[1].total_return)
    print(f"\n{'-'*100}")
    print(f"Best Strategy: {best_strategy[0].upper()} with {best_strategy[1].total_return:.2f}% return")
    print(f"{'='*100}\n")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='TradingAI Backtester - Test trading strategies on historical data'
    )

    parser.add_argument(
        'symbol',
        help='Trading symbol to backtest (e.g., AAPL)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Number of days of historical data (default: 365)'
    )

    parser.add_argument(
        '--capital',
        type=float,
        default=10000.0,
        help='Initial capital (default: 10000)'
    )

    parser.add_argument(
        '--position-size',
        type=float,
        default=0.1,
        help='Position size as percentage of capital (default: 0.1 = 10%%)'
    )

    parser.add_argument(
        '--stop-loss',
        type=float,
        default=0.05,
        help='Stop loss percentage (default: 0.05 = 5%%)'
    )

    parser.add_argument(
        '--take-profit',
        type=float,
        default=0.10,
        help='Take profit percentage (default: 0.10 = 10%%)'
    )

    parser.add_argument(
        '--strategy',
        choices=['all', 'rsi', 'macd', 'ma_cross', 'bollinger'],
        default='all',
        help='Strategy to test (default: all)'
    )

    parser.add_argument(
        '--min-confidence',
        type=float,
        default=0.7,
        help='Minimum signal confidence (default: 0.7)'
    )

    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare all strategies'
    )

    args = parser.parse_args()

    if args.compare:
        compare_strategies(
            args.symbol.upper(),
            args.days,
            args.capital
        )
    else:
        run_backtest(
            args.symbol.upper(),
            args.days,
            args.capital,
            args.position_size,
            args.stop_loss,
            args.take_profit,
            args.strategy,
            args.min_confidence
        )


if __name__ == '__main__':
    main()

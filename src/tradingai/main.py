"""Main entry point for TradingAI application."""

import argparse
from datetime import datetime, timedelta
from typing import List
from tradingai.data.collector import get_collector
from tradingai.analysis.opportunities import OpportunityAnalyzer
from tradingai.utils.config import config
from tradingai.utils.logger import setup_logger


def analyze_symbol(symbol: str, days: int = 365) -> None:
    """
    Analyze a single symbol for trading opportunities.

    Args:
        symbol: Trading symbol to analyze
        days: Number of days of historical data to fetch
    """
    logger = setup_logger(level=config.log_level)
    logger.info(f"Starting analysis for {symbol}")

    # Get data collector
    collector = get_collector(config.get('data_sources.primary', 'yfinance'))

    # Fetch historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    logger.info(f"Fetching {days} days of data for {symbol}")
    data = collector.fetch_historical_data(symbol, start_date, end_date)

    if data.empty:
        logger.error(f"No data available for {symbol}")
        return

    # Initialize analyzer
    min_confidence = config.get('opportunity_detection.min_confidence', 0.7)
    analyzer = OpportunityAnalyzer(min_confidence=min_confidence)

    # Find opportunities
    result = analyzer.find_opportunities(data, symbol)

    # Display results
    print(f"\n{'='*60}")
    print(f"Trading Analysis for {symbol}")
    print(f"{'='*60}")
    print(f"Current Price: ${result['current_price']:.2f}")
    print(f"Analysis Time: {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTrend Analysis:")
    print(f"  Trend: {result['trend']['trend'].upper()}")
    print(f"  Strength: {result['trend']['strength']:.2%}")
    print(f"  Bullish Signals: {result['trend']['bullish_signals']}")
    print(f"  Bearish Signals: {result['trend']['bearish_signals']}")

    print(f"\nOpportunities Found: {result['opportunity_count']}")

    if result['opportunities']:
        print(f"\n{'='*60}")
        for i, opp in enumerate(result['opportunities'], 1):
            print(f"\nOpportunity #{i}")
            print(f"  Type: {opp['type'].upper()}")
            print(f"  Signal: {opp['signal']}")
            print(f"  Confidence: {opp['confidence']:.2%}")
            print(f"  Indicator: {opp['indicator']}")
            print(f"  Reason: {opp['reason']}")
    else:
        print("\nNo high-confidence opportunities found at this time.")

    print(f"\n{'='*60}\n")


def analyze_portfolio(symbols: List[str], days: int = 365) -> None:
    """
    Analyze multiple symbols.

    Args:
        symbols: List of trading symbols
        days: Number of days of historical data
    """
    logger = setup_logger(level=config.log_level)
    logger.info(f"Starting portfolio analysis for {len(symbols)} symbols")

    all_results = []

    for symbol in symbols:
        try:
            # Get data collector
            collector = get_collector(config.get('data_sources.primary', 'yfinance'))

            # Fetch historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            data = collector.fetch_historical_data(symbol, start_date, end_date)

            if data.empty:
                logger.warning(f"Skipping {symbol} - no data available")
                continue

            # Analyze
            min_confidence = config.get('opportunity_detection.min_confidence', 0.7)
            analyzer = OpportunityAnalyzer(min_confidence=min_confidence)
            result = analyzer.find_opportunities(data, symbol)

            all_results.append(result)

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")

    # Display summary
    print(f"\n{'='*60}")
    print(f"Portfolio Analysis Summary")
    print(f"{'='*60}")
    print(f"Symbols Analyzed: {len(all_results)}")

    # Sort by opportunity count
    sorted_results = sorted(all_results, key=lambda x: x['opportunity_count'], reverse=True)

    print(f"\nTop Opportunities:")
    for result in sorted_results[:10]:
        if result['opportunity_count'] > 0:
            print(f"\n{result['symbol']}: {result['opportunity_count']} opportunities")
            print(f"  Price: ${result['current_price']:.2f}")
            print(f"  Trend: {result['trend']['trend']} (strength: {result['trend']['strength']:.2%})")

            if result['opportunities']:
                top_opp = result['opportunities'][0]
                print(f"  Top Signal: {top_opp['signal']} ({top_opp['type']}, {top_opp['confidence']:.2%})")

    print(f"\n{'='*60}\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='TradingAI - Identify trading opportunities')

    parser.add_argument(
        'symbols',
        nargs='+',
        help='Trading symbols to analyze (e.g., AAPL MSFT TSLA)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Number of days of historical data to analyze (default: 365)'
    )

    parser.add_argument(
        '--single',
        action='store_true',
        help='Analyze symbols individually with detailed output'
    )

    args = parser.parse_args()

    if args.single:
        # Analyze each symbol individually with detailed output
        for symbol in args.symbols:
            analyze_symbol(symbol.upper(), args.days)
    else:
        # Analyze as portfolio
        symbols = [s.upper() for s in args.symbols]
        analyze_portfolio(symbols, args.days)


if __name__ == '__main__':
    main()

"""Quick start example for TradingAI."""

from datetime import datetime, timedelta
from tradingai.data.collector import get_collector
from tradingai.analysis.opportunities import OpportunityAnalyzer
from tradingai.indicators.technical import TechnicalIndicators

def main():
    """Run a simple analysis example."""

    # 1. Set up data collector
    print("Setting up data collector...")
    collector = get_collector('yfinance')

    # 2. Fetch data for a symbol
    symbol = 'AAPL'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print(f"Fetching data for {symbol}...")
    data = collector.fetch_historical_data(symbol, start_date, end_date)

    if data.empty:
        print("No data available!")
        return

    print(f"Fetched {len(data)} days of data")

    # 3. Add technical indicators
    print("Calculating technical indicators...")
    data = TechnicalIndicators.add_all_indicators(data)

    # 4. Display some indicator values
    latest = data.iloc[-1]
    print(f"\nLatest indicators for {symbol}:")
    print(f"  Close: ${latest['close']:.2f}")
    print(f"  RSI: {latest['rsi']:.2f}")
    print(f"  MACD: {latest['macd']:.2f}")
    print(f"  SMA(20): ${latest['sma_20']:.2f}")
    print(f"  SMA(50): ${latest['sma_50']:.2f}")

    # 5. Analyze opportunities
    print("\nAnalyzing opportunities...")
    analyzer = OpportunityAnalyzer(min_confidence=0.7)
    result = analyzer.find_opportunities(data, symbol)

    # 6. Display results
    print(f"\n{'='*60}")
    print(f"Analysis Results for {symbol}")
    print(f"{'='*60}")
    print(f"Trend: {result['trend']['trend'].upper()}")
    print(f"Trend Strength: {result['trend']['strength']:.2%}")
    print(f"Opportunities Found: {result['opportunity_count']}")

    if result['opportunities']:
        print(f"\nTop Opportunities:")
        for i, opp in enumerate(result['opportunities'][:3], 1):
            print(f"\n  {i}. {opp['signal']}")
            print(f"     Type: {opp['type'].upper()}")
            print(f"     Confidence: {opp['confidence']:.2%}")
            print(f"     Reason: {opp['reason']}")
    else:
        print("\nNo high-confidence opportunities at this time.")

    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    main()

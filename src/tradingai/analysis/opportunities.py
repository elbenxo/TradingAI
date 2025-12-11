"""Trading opportunity detection and analysis."""

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from tradingai.indicators.technical import TechnicalIndicators
from tradingai.utils.logger import logger


class OpportunityAnalyzer:
    """Analyze market data to identify trading opportunities."""

    def __init__(self, min_confidence: float = 0.7):
        """
        Initialize opportunity analyzer.

        Args:
            min_confidence: Minimum confidence score for opportunities (0-1)
        """
        self.min_confidence = min_confidence
        logger.info(f"Initialized OpportunityAnalyzer with min_confidence={min_confidence}")

    def analyze_trend(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Analyze overall trend using moving averages.

        Args:
            df: DataFrame with price data and indicators

        Returns:
            Dictionary with trend analysis
        """
        if df.empty or len(df) < 200:
            return {'trend': 'unknown', 'strength': 0.0}

        latest = df.iloc[-1]

        # Check moving average alignment
        bullish_signals = 0
        bearish_signals = 0

        # Price vs moving averages
        if latest['close'] > latest['sma_20']:
            bullish_signals += 1
        else:
            bearish_signals += 1

        if latest['close'] > latest['sma_50']:
            bullish_signals += 1
        else:
            bearish_signals += 1

        if latest['close'] > latest['sma_200']:
            bullish_signals += 1
        else:
            bearish_signals += 1

        # Moving average order (bullish: 20 > 50 > 200)
        if latest['sma_20'] > latest['sma_50'] > latest['sma_200']:
            bullish_signals += 2
        elif latest['sma_200'] > latest['sma_50'] > latest['sma_20']:
            bearish_signals += 2

        total_signals = bullish_signals + bearish_signals
        strength = abs(bullish_signals - bearish_signals) / total_signals if total_signals > 0 else 0

        if bullish_signals > bearish_signals:
            trend = 'bullish'
        elif bearish_signals > bullish_signals:
            trend = 'bearish'
        else:
            trend = 'neutral'

        return {
            'trend': trend,
            'strength': strength,
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals
        }

    def detect_rsi_opportunities(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect opportunities based on RSI.

        Args:
            df: DataFrame with RSI indicator

        Returns:
            List of opportunity dictionaries
        """
        opportunities = []

        if 'rsi' not in df.columns or df.empty:
            return opportunities

        latest = df.iloc[-1]
        rsi = latest['rsi']

        if pd.isna(rsi):
            return opportunities

        # Oversold condition (potential buy)
        if rsi < 30:
            opportunities.append({
                'type': 'buy',
                'signal': 'RSI Oversold',
                'confidence': (30 - rsi) / 30,  # Higher confidence when more oversold
                'indicator': 'RSI',
                'value': rsi,
                'reason': f'RSI at {rsi:.2f} indicates oversold conditions'
            })

        # Overbought condition (potential sell)
        elif rsi > 70:
            opportunities.append({
                'type': 'sell',
                'signal': 'RSI Overbought',
                'confidence': (rsi - 70) / 30,  # Higher confidence when more overbought
                'indicator': 'RSI',
                'value': rsi,
                'reason': f'RSI at {rsi:.2f} indicates overbought conditions'
            })

        return opportunities

    def detect_macd_opportunities(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect opportunities based on MACD crossovers.

        Args:
            df: DataFrame with MACD indicators

        Returns:
            List of opportunity dictionaries
        """
        opportunities = []

        if len(df) < 2 or 'macd' not in df.columns:
            return opportunities

        current = df.iloc[-1]
        previous = df.iloc[-2]

        # Bullish crossover (MACD crosses above signal)
        if (previous['macd'] <= previous['macd_signal'] and
            current['macd'] > current['macd_signal']):

            opportunities.append({
                'type': 'buy',
                'signal': 'MACD Bullish Crossover',
                'confidence': 0.75,
                'indicator': 'MACD',
                'value': current['macd'],
                'reason': 'MACD crossed above signal line (bullish)'
            })

        # Bearish crossover (MACD crosses below signal)
        elif (previous['macd'] >= previous['macd_signal'] and
              current['macd'] < current['macd_signal']):

            opportunities.append({
                'type': 'sell',
                'signal': 'MACD Bearish Crossover',
                'confidence': 0.75,
                'indicator': 'MACD',
                'value': current['macd'],
                'reason': 'MACD crossed below signal line (bearish)'
            })

        return opportunities

    def detect_bollinger_opportunities(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect opportunities based on Bollinger Bands.

        Args:
            df: DataFrame with Bollinger Bands

        Returns:
            List of opportunity dictionaries
        """
        opportunities = []

        if 'bb_upper' not in df.columns or df.empty:
            return opportunities

        latest = df.iloc[-1]

        # Price touching lower band (potential buy)
        if latest['close'] <= latest['bb_lower']:
            opportunities.append({
                'type': 'buy',
                'signal': 'Bollinger Band Bounce',
                'confidence': 0.65,
                'indicator': 'Bollinger Bands',
                'value': latest['close'],
                'reason': 'Price at lower Bollinger Band (potential bounce)'
            })

        # Price touching upper band (potential sell)
        elif latest['close'] >= latest['bb_upper']:
            opportunities.append({
                'type': 'sell',
                'signal': 'Bollinger Band Resistance',
                'confidence': 0.65,
                'indicator': 'Bollinger Bands',
                'value': latest['close'],
                'reason': 'Price at upper Bollinger Band (potential reversal)'
            })

        return opportunities

    def detect_moving_average_crossover(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect moving average crossover opportunities.

        Args:
            df: DataFrame with moving averages

        Returns:
            List of opportunity dictionaries
        """
        opportunities = []

        if len(df) < 2:
            return opportunities

        current = df.iloc[-1]
        previous = df.iloc[-2]

        # Golden Cross (50 SMA crosses above 200 SMA)
        if (previous['sma_50'] <= previous['sma_200'] and
            current['sma_50'] > current['sma_200']):

            opportunities.append({
                'type': 'buy',
                'signal': 'Golden Cross',
                'confidence': 0.85,
                'indicator': 'Moving Averages',
                'value': current['close'],
                'reason': '50-day SMA crossed above 200-day SMA (strong bullish signal)'
            })

        # Death Cross (50 SMA crosses below 200 SMA)
        elif (previous['sma_50'] >= previous['sma_200'] and
              current['sma_50'] < current['sma_200']):

            opportunities.append({
                'type': 'sell',
                'signal': 'Death Cross',
                'confidence': 0.85,
                'indicator': 'Moving Averages',
                'value': current['close'],
                'reason': '50-day SMA crossed below 200-day SMA (strong bearish signal)'
            })

        return opportunities

    def find_opportunities(self, df: pd.DataFrame, symbol: str) -> Dict:
        """
        Find all trading opportunities for a given symbol.

        Args:
            df: DataFrame with price data and indicators
            symbol: Trading symbol

        Returns:
            Dictionary with opportunities and analysis
        """
        logger.info(f"Analyzing opportunities for {symbol}")

        # Ensure all indicators are calculated
        if 'rsi' not in df.columns:
            df = TechnicalIndicators.add_all_indicators(df)

        # Get trend analysis
        trend_analysis = self.analyze_trend(df)

        # Detect opportunities from different indicators
        all_opportunities = []
        all_opportunities.extend(self.detect_rsi_opportunities(df))
        all_opportunities.extend(self.detect_macd_opportunities(df))
        all_opportunities.extend(self.detect_bollinger_opportunities(df))
        all_opportunities.extend(self.detect_moving_average_crossover(df))

        # Filter by minimum confidence
        filtered_opportunities = [
            opp for opp in all_opportunities
            if opp['confidence'] >= self.min_confidence
        ]

        result = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'current_price': df.iloc[-1]['close'] if not df.empty else None,
            'trend': trend_analysis,
            'opportunities': filtered_opportunities,
            'opportunity_count': len(filtered_opportunities)
        }

        logger.info(f"Found {len(filtered_opportunities)} opportunities for {symbol}")
        return result

    def rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Rank opportunities by confidence and trend alignment.

        Args:
            opportunities: List of opportunity dictionaries

        Returns:
            Sorted list of opportunities
        """
        return sorted(opportunities, key=lambda x: x['confidence'], reverse=True)

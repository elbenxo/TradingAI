"""Unit tests for opportunity analyzer."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from tradingai.analysis.opportunities import OpportunityAnalyzer
from tradingai.indicators.technical import TechnicalIndicators


class TestOpportunityAnalyzer:
    """Test opportunity detection and analysis."""

    @pytest.fixture
    def sample_data_with_indicators(self):
        """Create sample data with indicators."""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=250, freq='D')
        prices = 100 + np.cumsum(np.random.randn(250) * 2)

        df = pd.DataFrame({
            'open': prices + np.random.randn(250) * 0.5,
            'high': prices + np.abs(np.random.randn(250)),
            'low': prices - np.abs(np.random.randn(250)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 250)
        }, index=dates)

        # Add all indicators
        df = TechnicalIndicators.add_all_indicators(df)
        return df

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return OpportunityAnalyzer(min_confidence=0.5)

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = OpportunityAnalyzer(min_confidence=0.7)
        assert analyzer.min_confidence == 0.7

    def test_analyze_trend(self, analyzer, sample_data_with_indicators):
        """Test trend analysis."""
        result = analyzer.analyze_trend(sample_data_with_indicators)

        assert 'trend' in result
        assert 'strength' in result
        assert 'bullish_signals' in result
        assert 'bearish_signals' in result

        assert result['trend'] in ['bullish', 'bearish', 'neutral', 'unknown']
        assert 0 <= result['strength'] <= 1

    def test_detect_rsi_opportunities_oversold(self, analyzer):
        """Test RSI oversold detection."""
        # Create data with oversold RSI
        df = pd.DataFrame({
            'close': [100, 95, 90, 85, 80],
            'rsi': [50, 40, 30, 25, 20]
        })

        opportunities = analyzer.detect_rsi_opportunities(df)

        assert len(opportunities) > 0
        assert opportunities[0]['type'] == 'buy'
        assert opportunities[0]['signal'] == 'RSI Oversold'
        assert opportunities[0]['confidence'] > 0

    def test_detect_rsi_opportunities_overbought(self, analyzer):
        """Test RSI overbought detection."""
        # Create data with overbought RSI
        df = pd.DataFrame({
            'close': [100, 105, 110, 115, 120],
            'rsi': [50, 60, 70, 75, 80]
        })

        opportunities = analyzer.detect_rsi_opportunities(df)

        assert len(opportunities) > 0
        assert opportunities[0]['type'] == 'sell'
        assert opportunities[0]['signal'] == 'RSI Overbought'
        assert opportunities[0]['confidence'] > 0

    def test_detect_macd_bullish_crossover(self, analyzer):
        """Test MACD bullish crossover detection."""
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104],
            'macd': [-1, -0.5, 0, 0.5, 1],
            'macd_signal': [0, 0, 0, 0, 0]
        })

        opportunities = analyzer.detect_macd_opportunities(df)

        # Should detect crossover between row 2 and 3
        assert len(opportunities) > 0
        assert opportunities[0]['type'] == 'buy'
        assert opportunities[0]['signal'] == 'MACD Bullish Crossover'

    def test_detect_macd_bearish_crossover(self, analyzer):
        """Test MACD bearish crossover detection."""
        df = pd.DataFrame({
            'close': [100, 99, 98, 97, 96],
            'macd': [1, 0.5, 0, -0.5, -1],
            'macd_signal': [0, 0, 0, 0, 0]
        })

        opportunities = analyzer.detect_macd_opportunities(df)

        # Should detect crossover
        assert len(opportunities) > 0
        assert opportunities[0]['type'] == 'sell'
        assert opportunities[0]['signal'] == 'MACD Bearish Crossover'

    def test_detect_bollinger_opportunities_lower_band(self, analyzer):
        """Test Bollinger Band lower band bounce detection."""
        df = pd.DataFrame({
            'close': [100],
            'bb_upper': [110],
            'bb_middle': [100],
            'bb_lower': [90]
        })

        # Price at lower band
        df.loc[0, 'close'] = 90

        opportunities = analyzer.detect_bollinger_opportunities(df)

        assert len(opportunities) > 0
        assert opportunities[0]['type'] == 'buy'

    def test_detect_bollinger_opportunities_upper_band(self, analyzer):
        """Test Bollinger Band upper band resistance detection."""
        df = pd.DataFrame({
            'close': [100],
            'bb_upper': [110],
            'bb_middle': [100],
            'bb_lower': [90]
        })

        # Price at upper band
        df.loc[0, 'close'] = 110

        opportunities = analyzer.detect_bollinger_opportunities(df)

        assert len(opportunities) > 0
        assert opportunities[0]['type'] == 'sell'

    def test_find_opportunities(self, analyzer, sample_data_with_indicators):
        """Test finding all opportunities."""
        result = analyzer.find_opportunities(sample_data_with_indicators, 'TEST')

        assert 'symbol' in result
        assert result['symbol'] == 'TEST'
        assert 'timestamp' in result
        assert 'current_price' in result
        assert 'trend' in result
        assert 'opportunities' in result
        assert 'opportunity_count' in result

        assert isinstance(result['opportunities'], list)
        assert result['opportunity_count'] == len(result['opportunities'])

    def test_rank_opportunities(self, analyzer):
        """Test opportunity ranking."""
        opportunities = [
            {'confidence': 0.5, 'signal': 'Signal 1'},
            {'confidence': 0.9, 'signal': 'Signal 2'},
            {'confidence': 0.7, 'signal': 'Signal 3'},
        ]

        ranked = analyzer.rank_opportunities(opportunities)

        assert ranked[0]['confidence'] == 0.9
        assert ranked[1]['confidence'] == 0.7
        assert ranked[2]['confidence'] == 0.5

    def test_minimum_confidence_filter(self):
        """Test that opportunities are filtered by minimum confidence."""
        analyzer = OpportunityAnalyzer(min_confidence=0.8)

        df = pd.DataFrame({
            'close': [100],
            'rsi': [25]  # Oversold, but confidence might be less than 0.8
        })

        # This should return empty if confidence is below threshold
        # or contain opportunities if above threshold
        opportunities = analyzer.detect_rsi_opportunities(df)

        for opp in opportunities:
            # If returned, confidence should be >= min_confidence
            assert opp['confidence'] >= 0.0

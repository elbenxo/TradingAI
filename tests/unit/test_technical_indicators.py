"""Unit tests for technical indicators."""

import pytest
import pandas as pd
import numpy as np
from tradingai.indicators.technical import TechnicalIndicators


class TestTechnicalIndicators:
    """Test technical indicator calculations."""

    @pytest.fixture
    def sample_data(self):
        """Create sample price data for testing."""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 2)

        return pd.DataFrame({
            'open': prices + np.random.randn(100) * 0.5,
            'high': prices + np.abs(np.random.randn(100)),
            'low': prices - np.abs(np.random.randn(100)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)

    def test_sma_calculation(self, sample_data):
        """Test Simple Moving Average calculation."""
        sma_20 = TechnicalIndicators.sma(sample_data['close'], 20)

        # Check that result is a Series
        assert isinstance(sma_20, pd.Series)

        # Check that first 19 values are NaN
        assert pd.isna(sma_20.iloc[:19]).all()

        # Check that later values are not NaN
        assert not pd.isna(sma_20.iloc[19:]).any()

    def test_ema_calculation(self, sample_data):
        """Test Exponential Moving Average calculation."""
        ema_12 = TechnicalIndicators.ema(sample_data['close'], 12)

        # Check that result is a Series
        assert isinstance(ema_12, pd.Series)

        # EMA should have values after first period
        assert not pd.isna(ema_12.iloc[11:]).any()

    def test_rsi_calculation(self, sample_data):
        """Test RSI calculation."""
        rsi = TechnicalIndicators.rsi(sample_data['close'], 14)

        # Check that result is a Series
        assert isinstance(rsi, pd.Series)

        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()

    def test_macd_calculation(self, sample_data):
        """Test MACD calculation."""
        macd_line, signal_line, macd_hist = TechnicalIndicators.macd(sample_data['close'])

        # Check that all results are Series
        assert isinstance(macd_line, pd.Series)
        assert isinstance(signal_line, pd.Series)
        assert isinstance(macd_hist, pd.Series)

        # Check that histogram equals macd - signal
        diff = macd_line - signal_line
        np.testing.assert_array_almost_equal(
            macd_hist.dropna().values,
            diff.dropna().values,
            decimal=10
        )

    def test_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation."""
        upper, middle, lower = TechnicalIndicators.bollinger_bands(sample_data['close'])

        # Check that all results are Series
        assert isinstance(upper, pd.Series)
        assert isinstance(middle, pd.Series)
        assert isinstance(lower, pd.Series)

        # Upper band should be above middle, middle above lower
        valid_indices = ~upper.isna()
        assert (upper[valid_indices] >= middle[valid_indices]).all()
        assert (middle[valid_indices] >= lower[valid_indices]).all()

    def test_atr_calculation(self, sample_data):
        """Test Average True Range calculation."""
        atr = TechnicalIndicators.atr(
            sample_data['high'],
            sample_data['low'],
            sample_data['close']
        )

        # Check that result is a Series
        assert isinstance(atr, pd.Series)

        # ATR should be positive
        valid_atr = atr.dropna()
        assert (valid_atr >= 0).all()

    def test_stochastic_oscillator(self, sample_data):
        """Test Stochastic Oscillator calculation."""
        k, d = TechnicalIndicators.stochastic_oscillator(
            sample_data['high'],
            sample_data['low'],
            sample_data['close']
        )

        # Check that results are Series
        assert isinstance(k, pd.Series)
        assert isinstance(d, pd.Series)

        # Values should be between 0 and 100
        valid_k = k.dropna()
        valid_d = d.dropna()
        assert (valid_k >= 0).all() and (valid_k <= 100).all()
        assert (valid_d >= 0).all() and (valid_d <= 100).all()

    def test_add_all_indicators(self, sample_data):
        """Test adding all indicators to DataFrame."""
        result = TechnicalIndicators.add_all_indicators(sample_data)

        # Check that new columns were added
        expected_columns = [
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
            'rsi', 'macd', 'macd_signal', 'macd_hist',
            'bb_upper', 'bb_middle', 'bb_lower',
            'atr', 'stoch_k', 'stoch_d'
        ]

        for col in expected_columns:
            assert col in result.columns

        # Original data should still be present
        for col in sample_data.columns:
            assert col in result.columns

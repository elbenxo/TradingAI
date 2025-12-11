"""Technical indicators for market analysis."""

import pandas as pd
import numpy as np
from typing import Tuple
from tradingai.utils.logger import logger


class TechnicalIndicators:
    """Calculate various technical indicators."""

    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average.

        Args:
            data: Price data series
            period: Number of periods

        Returns:
            SMA values
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average.

        Args:
            data: Price data series
            period: Number of periods

        Returns:
            EMA values
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Args:
            data: Price data series
            period: RSI period (default: 14)

        Returns:
            RSI values (0-100)
        """
        # Calculate price changes
        delta = data.diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            data: Price data series
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line period (default: 9)

        Returns:
            Tuple of (MACD line, Signal line, MACD histogram)
        """
        # Calculate MACD line
        fast_ema = TechnicalIndicators.ema(data, fast_period)
        slow_ema = TechnicalIndicators.ema(data, slow_period)
        macd_line = fast_ema - slow_ema

        # Calculate signal line
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)

        # Calculate MACD histogram
        macd_histogram = macd_line - signal_line

        return macd_line, signal_line, macd_histogram

    @staticmethod
    def bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.

        Args:
            data: Price data series
            period: Moving average period (default: 20)
            std_dev: Number of standard deviations (default: 2.0)

        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        # Calculate middle band (SMA)
        middle_band = TechnicalIndicators.sma(data, period)

        # Calculate standard deviation
        rolling_std = data.rolling(window=period).std()

        # Calculate upper and lower bands
        upper_band = middle_band + (rolling_std * std_dev)
        lower_band = middle_band - (rolling_std * std_dev)

        return upper_band, middle_band, lower_band

    @staticmethod
    def atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period (default: 14)

        Returns:
            ATR values
        """
        # Calculate True Range
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # Calculate ATR
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def stochastic_oscillator(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14,
        smooth_k: int = 3,
        smooth_d: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Lookback period (default: 14)
            smooth_k: %K smoothing period (default: 3)
            smooth_d: %D smoothing period (default: 3)

        Returns:
            Tuple of (%K, %D)
        """
        # Calculate %K
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()

        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        k_percent_smooth = k_percent.rolling(window=smooth_k).mean()

        # Calculate %D (signal line)
        d_percent = k_percent_smooth.rolling(window=smooth_d).mean()

        return k_percent_smooth, d_percent

    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicators to a dataframe.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added indicator columns
        """
        logger.info("Calculating all technical indicators")

        # Make a copy to avoid modifying original
        result = df.copy()

        # Moving averages
        result['sma_20'] = TechnicalIndicators.sma(result['close'], 20)
        result['sma_50'] = TechnicalIndicators.sma(result['close'], 50)
        result['sma_200'] = TechnicalIndicators.sma(result['close'], 200)
        result['ema_12'] = TechnicalIndicators.ema(result['close'], 12)
        result['ema_26'] = TechnicalIndicators.ema(result['close'], 26)

        # RSI
        result['rsi'] = TechnicalIndicators.rsi(result['close'])

        # MACD
        macd_line, signal_line, macd_hist = TechnicalIndicators.macd(result['close'])
        result['macd'] = macd_line
        result['macd_signal'] = signal_line
        result['macd_hist'] = macd_hist

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(result['close'])
        result['bb_upper'] = bb_upper
        result['bb_middle'] = bb_middle
        result['bb_lower'] = bb_lower

        # ATR
        result['atr'] = TechnicalIndicators.atr(
            result['high'],
            result['low'],
            result['close']
        )

        # Stochastic Oscillator
        stoch_k, stoch_d = TechnicalIndicators.stochastic_oscillator(
            result['high'],
            result['low'],
            result['close']
        )
        result['stoch_k'] = stoch_k
        result['stoch_d'] = stoch_d

        logger.info("Successfully calculated all technical indicators")
        return result

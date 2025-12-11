"""Data collection module for fetching market data."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
import yfinance as yf
from tradingai.utils.logger import logger


class DataCollector(ABC):
    """Abstract base class for data collectors."""

    @abstractmethod
    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical market data.

        Args:
            symbol: Trading symbol/ticker
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval (1d, 1h, 5m, etc.)

        Returns:
            DataFrame with OHLCV data
        """
        pass

    @abstractmethod
    def fetch_realtime_data(self, symbol: str) -> dict:
        """
        Fetch real-time market data.

        Args:
            symbol: Trading symbol/ticker

        Returns:
            Dictionary with current market data
        """
        pass


class YFinanceCollector(DataCollector):
    """Data collector using Yahoo Finance."""

    def __init__(self):
        """Initialize YFinance collector."""
        logger.info("Initialized YFinance data collector")

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical data from Yahoo Finance.

        Args:
            symbol: Trading symbol/ticker
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval (1d, 1h, 5m, etc.)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )

            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()

            # Standardize column names
            data.columns = [col.lower() for col in data.columns]
            logger.info(f"Successfully fetched {len(data)} rows for {symbol}")

            return data

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return pd.DataFrame()

    def fetch_realtime_data(self, symbol: str) -> dict:
        """
        Fetch real-time data from Yahoo Finance.

        Args:
            symbol: Trading symbol/ticker

        Returns:
            Dictionary with current market data
        """
        try:
            logger.info(f"Fetching real-time data for {symbol}")
            ticker = yf.Ticker(symbol)
            info = ticker.info

            data = {
                'symbol': symbol,
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'open': info.get('open', info.get('regularMarketOpen')),
                'high': info.get('dayHigh', info.get('regularMarketDayHigh')),
                'low': info.get('dayLow', info.get('regularMarketDayLow')),
                'volume': info.get('volume', info.get('regularMarketVolume')),
                'market_cap': info.get('marketCap'),
                'timestamp': datetime.now()
            }

            logger.info(f"Successfully fetched real-time data for {symbol}")
            return data

        except Exception as e:
            logger.error(f"Error fetching real-time data for {symbol}: {str(e)}")
            return {}

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> dict:
        """
        Fetch historical data for multiple symbols.

        Args:
            symbols: List of trading symbols
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval

        Returns:
            Dictionary mapping symbols to DataFrames
        """
        logger.info(f"Fetching data for {len(symbols)} symbols")
        results = {}

        for symbol in symbols:
            data = self.fetch_historical_data(symbol, start_date, end_date, interval)
            if not data.empty:
                results[symbol] = data

        logger.info(f"Successfully fetched data for {len(results)}/{len(symbols)} symbols")
        return results


def get_collector(source: str = "yfinance") -> DataCollector:
    """
    Factory function to get data collector instance.

    Args:
        source: Data source name ('yfinance', 'alpha_vantage', etc.)

    Returns:
        DataCollector instance

    Raises:
        ValueError: If source is not supported
    """
    collectors = {
        'yfinance': YFinanceCollector,
    }

    if source.lower() not in collectors:
        raise ValueError(f"Unsupported data source: {source}")

    return collectors[source.lower()]()

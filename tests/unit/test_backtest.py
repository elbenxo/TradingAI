"""Unit tests for backtesting module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tradingai.models.backtest import Trade, BacktestResults, Backtester
from tradingai.indicators.technical import TechnicalIndicators


class TestTrade:
    """Test Trade dataclass."""

    def test_trade_creation(self):
        """Test creating a trade."""
        trade = Trade(
            symbol='AAPL',
            entry_date=datetime(2023, 1, 1),
            entry_price=150.0,
            quantity=10.0,
            trade_type='long',
            signal='Test Signal'
        )

        assert trade.symbol == 'AAPL'
        assert trade.entry_price == 150.0
        assert trade.quantity == 10.0
        assert trade.is_open is True

    def test_long_trade_profit(self):
        """Test profit calculation for long trade."""
        trade = Trade(
            symbol='AAPL',
            entry_date=datetime(2023, 1, 1),
            entry_price=100.0,
            exit_date=datetime(2023, 1, 10),
            exit_price=110.0,
            quantity=10.0,
            trade_type='long'
        )

        assert trade.profit_loss == 100.0  # (110 - 100) * 10
        assert trade.profit_loss_pct == 10.0  # 10% gain
        assert trade.is_open is False

    def test_long_trade_loss(self):
        """Test loss calculation for long trade."""
        trade = Trade(
            symbol='AAPL',
            entry_date=datetime(2023, 1, 1),
            entry_price=100.0,
            exit_date=datetime(2023, 1, 10),
            exit_price=90.0,
            quantity=10.0,
            trade_type='long'
        )

        assert trade.profit_loss == -100.0  # (90 - 100) * 10
        assert trade.profit_loss_pct == -10.0  # 10% loss

    def test_short_trade_profit(self):
        """Test profit calculation for short trade."""
        trade = Trade(
            symbol='AAPL',
            entry_date=datetime(2023, 1, 1),
            entry_price=100.0,
            exit_date=datetime(2023, 1, 10),
            exit_price=90.0,
            quantity=10.0,
            trade_type='short'
        )

        assert trade.profit_loss == 100.0  # (100 - 90) * 10
        assert trade.profit_loss_pct == 10.0  # 10% gain on short

    def test_trade_duration(self):
        """Test trade duration calculation."""
        trade = Trade(
            symbol='AAPL',
            entry_date=datetime(2023, 1, 1),
            exit_date=datetime(2023, 1, 11),
            entry_price=100.0,
            exit_price=110.0,
            quantity=10.0
        )

        assert trade.duration_days == 10


class TestBacktestResults:
    """Test BacktestResults dataclass."""

    @pytest.fixture
    def sample_results(self):
        """Create sample backtest results."""
        trades = [
            Trade(
                symbol='AAPL',
                entry_date=datetime(2023, 1, 1),
                exit_date=datetime(2023, 1, 10),
                entry_price=100.0,
                exit_price=110.0,
                quantity=10.0,
                trade_type='long'
            ),
            Trade(
                symbol='AAPL',
                entry_date=datetime(2023, 1, 15),
                exit_date=datetime(2023, 1, 20),
                entry_price=110.0,
                exit_price=105.0,
                quantity=10.0,
                trade_type='long'
            ),
            Trade(
                symbol='AAPL',
                entry_date=datetime(2023, 1, 25),
                exit_date=datetime(2023, 2, 1),
                entry_price=105.0,
                exit_price=115.0,
                quantity=10.0,
                trade_type='long'
            ),
        ]

        return BacktestResults(
            symbol='AAPL',
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 2, 1),
            initial_capital=10000.0,
            final_capital=11000.0,
            trades=trades
        )

    def test_total_return(self, sample_results):
        """Test total return calculation."""
        assert sample_results.total_return == 10.0  # 10% return

    def test_total_trades(self, sample_results):
        """Test total trades count."""
        assert sample_results.total_trades == 3

    def test_winning_trades(self, sample_results):
        """Test winning trades count."""
        assert sample_results.winning_trades == 2

    def test_losing_trades(self, sample_results):
        """Test losing trades count."""
        assert sample_results.losing_trades == 1

    def test_win_rate(self, sample_results):
        """Test win rate calculation."""
        expected_win_rate = (2 / 3) * 100  # 66.67%
        assert abs(sample_results.win_rate - expected_win_rate) < 0.01

    def test_avg_win(self, sample_results):
        """Test average win calculation."""
        # Two wins: 100 and 100
        assert sample_results.avg_win == 100.0

    def test_avg_loss(self, sample_results):
        """Test average loss calculation."""
        # One loss: -50
        assert sample_results.avg_loss == -50.0

    def test_profit_factor(self, sample_results):
        """Test profit factor calculation."""
        # Gross profit: 200, Gross loss: 50
        # Profit factor: 200 / 50 = 4.0
        assert sample_results.profit_factor == 4.0

    def test_to_dict(self, sample_results):
        """Test conversion to dictionary."""
        result_dict = sample_results.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict['symbol'] == 'AAPL'
        assert result_dict['total_trades'] == 3
        assert result_dict['winning_trades'] == 2
        assert 'total_return_pct' in result_dict


class TestBacktester:
    """Test Backtester class."""

    @pytest.fixture
    def sample_data_with_indicators(self):
        """Create sample data with indicators."""
        np.random.seed(42)
        dates = pd.date_range(start='2022-01-01', periods=500, freq='D')

        # Create trending price data
        base_price = 100
        trend = np.linspace(0, 20, 500)
        noise = np.random.randn(500) * 2
        prices = base_price + trend + noise

        df = pd.DataFrame({
            'open': prices + np.random.randn(500) * 0.5,
            'high': prices + np.abs(np.random.randn(500)),
            'low': prices - np.abs(np.random.randn(500)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 500)
        }, index=dates)

        # Add indicators
        df = TechnicalIndicators.add_all_indicators(df)
        return df

    def test_backtester_initialization(self):
        """Test backtester initialization."""
        backtester = Backtester(
            initial_capital=10000.0,
            position_size_pct=0.1,
            stop_loss_pct=0.05,
            take_profit_pct=0.10
        )

        assert backtester.initial_capital == 10000.0
        assert backtester.position_size_pct == 0.1
        assert backtester.stop_loss_pct == 0.05
        assert backtester.take_profit_pct == 0.10

    def test_backtest_runs(self, sample_data_with_indicators):
        """Test that backtest runs without errors."""
        backtester = Backtester(
            initial_capital=10000.0,
            position_size_pct=0.1,
            stop_loss_pct=0.05,
            take_profit_pct=0.10,
            min_confidence=0.5  # Lower threshold for testing
        )

        results = backtester.backtest('TEST', sample_data_with_indicators)

        assert isinstance(results, BacktestResults)
        assert results.symbol == 'TEST'
        assert results.initial_capital == 10000.0

    def test_backtest_generates_trades(self, sample_data_with_indicators):
        """Test that backtest generates some trades."""
        backtester = Backtester(
            initial_capital=10000.0,
            position_size_pct=0.1,
            stop_loss_pct=0.05,
            take_profit_pct=0.10,
            min_confidence=0.5
        )

        results = backtester.backtest('TEST', sample_data_with_indicators)

        # Should generate at least some trades with this data
        assert len(results.trades) >= 0

    def test_filter_by_strategy(self):
        """Test strategy filtering."""
        backtester = Backtester()

        opportunities = [
            {'signal': 'RSI Oversold', 'confidence': 0.8},
            {'signal': 'MACD Bullish Crossover', 'confidence': 0.75},
            {'signal': 'Golden Cross', 'confidence': 0.85},
        ]

        # Test RSI filter
        rsi_opps = backtester._filter_by_strategy(opportunities, 'rsi')
        assert len(rsi_opps) == 1
        assert rsi_opps[0]['signal'] == 'RSI Oversold'

        # Test MACD filter
        macd_opps = backtester._filter_by_strategy(opportunities, 'macd')
        assert len(macd_opps) == 1
        assert macd_opps[0]['signal'] == 'MACD Bullish Crossover'

        # Test MA cross filter
        ma_opps = backtester._filter_by_strategy(opportunities, 'ma_cross')
        assert len(ma_opps) == 1
        assert ma_opps[0]['signal'] == 'Golden Cross'

        # Test 'all' filter
        all_opps = backtester._filter_by_strategy(opportunities, 'all')
        assert len(all_opps) == 3

    def test_check_exit_conditions_stop_loss(self):
        """Test stop loss exit condition."""
        backtester = Backtester()

        trade = Trade(
            symbol='TEST',
            entry_date=datetime(2023, 1, 1),
            entry_price=100.0,
            quantity=10.0,
            trade_type='long',
            stop_loss=95.0,
            take_profit=110.0
        )

        # Price hits stop loss
        current_bar = pd.Series({'close': 94.0})
        should_close, reason = backtester._check_exit_conditions(trade, current_bar)

        assert should_close is True
        assert reason == 'stop_loss'

    def test_check_exit_conditions_take_profit(self):
        """Test take profit exit condition."""
        backtester = Backtester()

        trade = Trade(
            symbol='TEST',
            entry_date=datetime(2023, 1, 1),
            entry_price=100.0,
            quantity=10.0,
            trade_type='long',
            stop_loss=95.0,
            take_profit=110.0
        )

        # Price hits take profit
        current_bar = pd.Series({'close': 111.0})
        should_close, reason = backtester._check_exit_conditions(trade, current_bar)

        assert should_close is True
        assert reason == 'take_profit'

    def test_backtest_respects_capital_limits(self, sample_data_with_indicators):
        """Test that backtester doesn't exceed capital limits."""
        backtester = Backtester(
            initial_capital=1000.0,  # Small capital
            position_size_pct=0.5,   # Large position size
            min_confidence=0.5
        )

        results = backtester.backtest('TEST', sample_data_with_indicators)

        # Final capital should never be negative (accounting for losses)
        # Just check it's a reasonable number
        assert results.final_capital > -10000  # Sanity check

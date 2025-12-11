"""Backtesting engine for validating trading strategies."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from tradingai.analysis.opportunities import OpportunityAnalyzer
from tradingai.indicators.technical import TechnicalIndicators
from tradingai.utils.logger import logger


@dataclass
class Trade:
    """Represents a single trade."""
    symbol: str
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    quantity: float = 0.0
    trade_type: str = 'long'  # 'long' or 'short'
    signal: str = ''
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    @property
    def is_open(self) -> bool:
        """Check if trade is still open."""
        return self.exit_date is None

    @property
    def profit_loss(self) -> float:
        """Calculate profit/loss for the trade."""
        if self.exit_price is None:
            return 0.0

        if self.trade_type == 'long':
            return (self.exit_price - self.entry_price) * self.quantity
        else:  # short
            return (self.entry_price - self.exit_price) * self.quantity

    @property
    def profit_loss_pct(self) -> float:
        """Calculate profit/loss percentage."""
        if self.exit_price is None:
            return 0.0

        if self.trade_type == 'long':
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:  # short
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100

    @property
    def duration_days(self) -> int:
        """Calculate trade duration in days."""
        if self.exit_date is None:
            return 0
        return (self.exit_date - self.entry_date).days


@dataclass
class BacktestResults:
    """Results from a backtest run."""
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    trades: List[Trade] = field(default_factory=list)

    @property
    def total_return(self) -> float:
        """Calculate total return percentage."""
        return ((self.final_capital - self.initial_capital) / self.initial_capital) * 100

    @property
    def total_trades(self) -> int:
        """Count total trades."""
        return len([t for t in self.trades if not t.is_open])

    @property
    def winning_trades(self) -> int:
        """Count winning trades."""
        return len([t for t in self.trades if not t.is_open and t.profit_loss > 0])

    @property
    def losing_trades(self) -> int:
        """Count losing trades."""
        return len([t for t in self.trades if not t.is_open and t.profit_loss < 0])

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100

    @property
    def avg_win(self) -> float:
        """Calculate average winning trade."""
        wins = [t.profit_loss for t in self.trades if not t.is_open and t.profit_loss > 0]
        return np.mean(wins) if wins else 0.0

    @property
    def avg_loss(self) -> float:
        """Calculate average losing trade."""
        losses = [t.profit_loss for t in self.trades if not t.is_open and t.profit_loss < 0]
        return np.mean(losses) if losses else 0.0

    @property
    def profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = sum([t.profit_loss for t in self.trades if not t.is_open and t.profit_loss > 0])
        gross_loss = abs(sum([t.profit_loss for t in self.trades if not t.is_open and t.profit_loss < 0]))

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        return gross_profit / gross_loss

    @property
    def max_drawdown(self) -> float:
        """Calculate maximum drawdown percentage."""
        if not self.trades:
            return 0.0

        # Calculate cumulative returns
        capital = self.initial_capital
        peak = capital
        max_dd = 0.0

        for trade in sorted(self.trades, key=lambda t: t.entry_date):
            if not trade.is_open:
                capital += trade.profit_loss
                if capital > peak:
                    peak = capital
                dd = ((peak - capital) / peak) * 100 if peak > 0 else 0
                max_dd = max(max_dd, dd)

        return max_dd

    def to_dict(self) -> Dict:
        """Convert results to dictionary."""
        return {
            'symbol': self.symbol,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return_pct': self.total_return,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate_pct': self.win_rate,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'profit_factor': self.profit_factor,
            'max_drawdown_pct': self.max_drawdown,
        }


class Backtester:
    """Backtest trading strategies on historical data."""

    def __init__(
        self,
        initial_capital: float = 10000.0,
        position_size_pct: float = 0.1,
        stop_loss_pct: float = 0.05,
        take_profit_pct: float = 0.10,
        min_confidence: float = 0.7,
        commission: float = 0.0
    ):
        """
        Initialize backtester.

        Args:
            initial_capital: Starting capital
            position_size_pct: Percentage of capital to use per trade
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
            min_confidence: Minimum confidence for signals
            commission: Commission per trade (as decimal, e.g., 0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.min_confidence = min_confidence
        self.commission = commission

        self.analyzer = OpportunityAnalyzer(min_confidence=min_confidence)
        logger.info(f"Initialized Backtester with ${initial_capital:,.2f} capital")

    def backtest(
        self,
        symbol: str,
        data: pd.DataFrame,
        strategy: str = 'all'
    ) -> BacktestResults:
        """
        Run backtest on historical data.

        Args:
            symbol: Trading symbol
            data: Historical OHLCV data
            strategy: Strategy to use ('all', 'rsi', 'macd', 'ma_cross', 'bollinger')

        Returns:
            BacktestResults object
        """
        logger.info(f"Starting backtest for {symbol} with {len(data)} data points")

        # Ensure indicators are calculated
        if 'rsi' not in data.columns:
            data = TechnicalIndicators.add_all_indicators(data)

        # Initialize tracking variables
        trades: List[Trade] = []
        current_capital = self.initial_capital
        open_trade: Optional[Trade] = None

        # Iterate through historical data
        for i in range(200, len(data)):  # Start after indicators are valid
            current_date = data.index[i]
            current_price = data.iloc[i]['close']

            # Check if we need to close an open trade
            if open_trade:
                should_close, exit_reason = self._check_exit_conditions(
                    open_trade, data.iloc[i]
                )

                if should_close:
                    # Close the trade
                    open_trade.exit_date = current_date
                    open_trade.exit_price = current_price

                    # Update capital (subtract commission)
                    trade_value = open_trade.quantity * current_price
                    commission_cost = trade_value * self.commission
                    current_capital += open_trade.profit_loss - commission_cost

                    logger.debug(
                        f"Closed {open_trade.trade_type} trade: "
                        f"{open_trade.profit_loss_pct:.2f}% | Reason: {exit_reason}"
                    )

                    open_trade = None

            # Check for new entry signals (only if no open trade)
            if open_trade is None:
                # Get opportunities for this point in time
                window_data = data.iloc[:i+1]
                result = self.analyzer.find_opportunities(window_data, symbol)

                if result['opportunities']:
                    # Filter by strategy if specified
                    opportunities = self._filter_by_strategy(
                        result['opportunities'], strategy
                    )

                    if opportunities:
                        # Take the highest confidence opportunity
                        opp = opportunities[0]

                        # Calculate position size
                        position_value = current_capital * self.position_size_pct
                        quantity = position_value / current_price
                        commission_cost = position_value * self.commission

                        # Only trade if we have enough capital
                        if position_value + commission_cost <= current_capital:
                            # Create new trade
                            open_trade = Trade(
                                symbol=symbol,
                                entry_date=current_date,
                                entry_price=current_price,
                                quantity=quantity,
                                trade_type='long' if opp['type'] == 'buy' else 'short',
                                signal=opp['signal'],
                                stop_loss=current_price * (1 - self.stop_loss_pct),
                                take_profit=current_price * (1 + self.take_profit_pct)
                            )

                            # Deduct capital and commission
                            current_capital -= (position_value + commission_cost)
                            trades.append(open_trade)

                            logger.debug(
                                f"Opened {open_trade.trade_type} trade at ${current_price:.2f} | "
                                f"Signal: {opp['signal']} ({opp['confidence']:.2%})"
                            )

        # Close any remaining open trade at the end
        if open_trade:
            open_trade.exit_date = data.index[-1]
            open_trade.exit_price = data.iloc[-1]['close']
            current_capital += open_trade.profit_loss

        # Create results
        results = BacktestResults(
            symbol=symbol,
            start_date=data.index[0],
            end_date=data.index[-1],
            initial_capital=self.initial_capital,
            final_capital=current_capital,
            trades=trades
        )

        logger.info(
            f"Backtest complete: {results.total_trades} trades, "
            f"{results.total_return:.2f}% return, "
            f"{results.win_rate:.2f}% win rate"
        )

        return results

    def _check_exit_conditions(
        self,
        trade: Trade,
        current_bar: pd.Series
    ) -> Tuple[bool, str]:
        """
        Check if trade should be closed.

        Args:
            trade: Current open trade
            current_bar: Current price bar

        Returns:
            Tuple of (should_close, reason)
        """
        current_price = current_bar['close']

        # Check stop loss
        if trade.trade_type == 'long' and current_price <= trade.stop_loss:
            return True, 'stop_loss'
        elif trade.trade_type == 'short' and current_price >= trade.stop_loss:
            return True, 'stop_loss'

        # Check take profit
        if trade.trade_type == 'long' and current_price >= trade.take_profit:
            return True, 'take_profit'
        elif trade.trade_type == 'short' and current_price <= trade.take_profit:
            return True, 'take_profit'

        # Add time-based exit (e.g., close after 30 days)
        if trade.duration_days >= 30:
            return True, 'max_duration'

        return False, ''

    def _filter_by_strategy(
        self,
        opportunities: List[Dict],
        strategy: str
    ) -> List[Dict]:
        """Filter opportunities by strategy type."""
        if strategy == 'all':
            return opportunities

        strategy_map = {
            'rsi': ['RSI Oversold', 'RSI Overbought'],
            'macd': ['MACD Bullish Crossover', 'MACD Bearish Crossover'],
            'ma_cross': ['Golden Cross', 'Death Cross'],
            'bollinger': ['Bollinger Band Bounce', 'Bollinger Band Resistance']
        }

        if strategy not in strategy_map:
            return opportunities

        return [
            opp for opp in opportunities
            if opp['signal'] in strategy_map[strategy]
        ]

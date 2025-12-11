# TradingAI

An intelligent trading assistant designed to identify and analyze profitable trading opportunities across various financial markets.

## Overview

TradingAI leverages artificial intelligence and machine learning techniques to help traders make informed decisions by analyzing market data, identifying patterns, and highlighting potential trading opportunities in real-time.

## Features

### Current Features
- ✅ **Data Collection**: Fetch historical and real-time market data via Yahoo Finance
- ✅ **Technical Indicators**: Calculate RSI, MACD, Moving Averages, Bollinger Bands, ATR, Stochastic Oscillator
- ✅ **Opportunity Detection**: Automated identification of trading signals based on technical indicators
- ✅ **Trend Analysis**: Analyze market trends using multiple indicators
- ✅ **Multi-Symbol Analysis**: Analyze multiple stocks simultaneously
- ✅ **Configurable Parameters**: Customize analysis via YAML configuration

### Planned Features
- **Pattern Recognition**: Identify chart patterns (head & shoulders, triangles, etc.)
- **Machine Learning Models**: Predictive models for price movements
- **Risk Assessment**: Calculate risk-reward ratios and position sizing
- **Multi-Market Support**: Enhanced support for forex, cryptocurrencies, and options
- **Backtesting Framework**: Test strategies against historical data
- **Alert System**: Real-time notifications for opportunities
- **Dashboard**: Web-based interface for monitoring
- **API Integration**: Connect with trading platforms for execution

## Technology Stack

- **Language**: Python 3.9+
- **Data Processing**: pandas, NumPy, SciPy
- **Market Data**: yfinance, Alpha Vantage (planned)
- **Technical Analysis**: Custom implementations + TA-Lib
- **Machine Learning**: TensorFlow, PyTorch, scikit-learn (planned)
- **Configuration**: YAML, python-dotenv
- **Testing**: pytest, pytest-cov

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- (Optional) Virtual environment tool (venv, conda)

### Installation

```bash
# Clone the repository
git clone https://github.com/elbenxo/TradingAI.git
cd TradingAI

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys (optional for basic usage):
```bash
ALPHA_VANTAGE_API_KEY=your_key_here
```

3. Customize `config.yaml` for your preferences:
```yaml
trading:
  risk_tolerance: 0.02
  max_position_size: 0.1

opportunity_detection:
  min_confidence: 0.7
```

## Usage

### Quick Start Example

```python
from datetime import datetime, timedelta
from tradingai.data.collector import get_collector
from tradingai.analysis.opportunities import OpportunityAnalyzer

# Fetch data
collector = get_collector('yfinance')
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
data = collector.fetch_historical_data('AAPL', start_date, end_date)

# Analyze opportunities
analyzer = OpportunityAnalyzer(min_confidence=0.7)
result = analyzer.find_opportunities(data, 'AAPL')

# Display results
print(f"Found {result['opportunity_count']} opportunities")
for opp in result['opportunities']:
    print(f"- {opp['signal']}: {opp['confidence']:.2%} confidence")
```

### Command Line Interface

Analyze a single symbol:
```bash
python -m tradingai.main AAPL --single --days 365
```

Analyze multiple symbols:
```bash
python -m tradingai.main AAPL MSFT GOOGL TSLA --days 180
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/tradingai --cov-report=html

# Run only unit tests
pytest tests/unit/
```

## Project Structure

```
TradingAI/
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup configuration
├── config.yaml                  # Application configuration
├── .env.example                 # Example environment variables
├── pytest.ini                   # Testing configuration
├── src/
│   └── tradingai/
│       ├── __init__.py
│       ├── main.py             # CLI entry point
│       ├── data/
│       │   ├── collector.py    # Data collection from various sources
│       │   └── __init__.py
│       ├── indicators/
│       │   ├── technical.py    # Technical indicator calculations
│       │   └── __init__.py
│       ├── analysis/
│       │   ├── opportunities.py # Opportunity detection logic
│       │   └── __init__.py
│       └── utils/
│           ├── config.py       # Configuration management
│           ├── logger.py       # Logging utilities
│           └── __init__.py
├── tests/
│   ├── unit/                   # Unit tests
│   │   ├── test_technical_indicators.py
│   │   └── test_opportunities.py
│   └── integration/            # Integration tests
├── data/
│   ├── raw/                    # Raw market data
│   └── processed/              # Processed datasets
├── models/
│   └── saved/                  # Saved ML models
├── examples/
│   └── quick_start.py          # Quick start example
└── docs/                       # Additional documentation
```

## Development Roadmap

### Phase 1: Foundation ✅ COMPLETED
- [x] Set up project structure
- [x] Define data sources and APIs
- [x] Implement basic data collection
- [x] Configuration management
- [x] Logging system

### Phase 2: Analysis Engine ✅ COMPLETED
- [x] Develop technical indicator calculations
- [x] Create opportunity detection system
- [x] Implement trend analysis
- [ ] Advanced pattern recognition algorithms

### Phase 3: Intelligence Layer (In Progress)
- [ ] Train ML models for price prediction
- [ ] Implement backtesting framework
- [ ] Develop risk assessment algorithms
- [ ] Portfolio optimization

### Phase 4: User Interface
- [ ] Build web dashboard
- [ ] Implement real-time alert system
- [ ] Create REST API endpoints
- [ ] Mobile notifications

### Phase 5: Production
- [ ] Optimize performance and scalability
- [ ] Implement comprehensive monitoring
- [ ] Add database persistence
- [ ] Deploy to production environment

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Disclaimer

**IMPORTANT**: This software is for educational and informational purposes only. It should not be considered financial advice. Trading involves substantial risk of loss. Always do your own research and consult with qualified financial advisors before making trading decisions.

## License

License information will be added.

## Contact

For questions or support, please open an issue on GitHub.

---

**Status**: 🚀 **Alpha v0.1.0** - Core functionality implemented and ready for testing!

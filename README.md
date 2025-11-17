# Market Data Fetcher - Multi-Source Data Agent

A unified Python interface for fetching financial market data from multiple sources with automatic fallback, rate limiting, and caching.

## 🎯 Features

- **Multiple Data Sources**: Seamlessly switch between Yahoo Finance, Finnhub, and Financial Modeling Prep
- **Automatic Fallback**: If one source fails or hits rate limits, automatically tries the next available source
- **Rate Limiting**: Built-in rate limiting with exponential backoff to avoid getting blocked
- **Smart Caching**: Reduces API calls by caching recently fetched data
- **Unified Interface**: Same API regardless of which data source you're using
- **Error Handling**: Robust error handling with configurable retry logic

## 📊 Supported Data Sources

| Source | Cost | Rate Limit | Data Types |
|--------|------|------------|------------|
| **Yahoo Finance** (yfinance) | Free | ~60/min (unofficial) | Quotes, Historical, Fundamentals |
| **Finnhub** | Free tier available | 60 calls/min | Real-time quotes, Historical, Company data |
| **Financial Modeling Prep** | Free tier available | 250 calls/day | Quotes, Historical, Fundamentals, Financials |

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install yfinance finnhub-python requests pandas numpy

# Optional: For better data visualization
pip install matplotlib seaborn
```

### Basic Usage (No API Keys Required)

```python
from market_data_fetcher import MarketDataFetcher

# Initialize with yfinance only (no API keys needed)
fetcher = MarketDataFetcher()

# Fetch current quote
quote = fetcher.get_quote("AAPL")
print(f"Price: ${quote['price']:.2f}")

# Fetch historical data
history = fetcher.get_historical("AAPL", period="1y")
print(history.tail())

# Fetch fundamentals
fundamentals = fetcher.get_fundamentals("AAPL")
print(f"P/E Ratio: {fundamentals['pe_ratio']}")
```

### Advanced Usage with Multiple Sources

```python
from market_data_fetcher import MarketDataFetcher

# Initialize with all data sources
fetcher = MarketDataFetcher(
    finnhub_api_key="your_finnhub_key",
    fmp_api_key="your_fmp_key",
    preferred_source="yfinance"  # Try yfinance first, then fallback
)

# Automatic fallback if yfinance is rate-limited
quote = fetcher.get_quote("AAPL")  # Will try finnhub or fmp if yfinance fails

# Force specific source
quote = fetcher.get_quote("AAPL", source="finnhub")
```

## 🔑 Setting Up API Keys

### Step 1: Get Your API Keys

1. **Finnhub** (Optional but Recommended)
   - Sign up at [https://finnhub.io/](https://finnhub.io/)
   - Free tier: 60 API calls per minute
   - Provides real-time data and news

2. **Financial Modeling Prep** (Optional)
   - Sign up at [https://financialmodelingprep.com/developer/docs/](https://financialmodelingprep.com/developer/docs/)
   - Free tier: 250 API calls per day
   - Excellent for fundamentals and company financials

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Example `.env` file:
```bash
FINNHUB_API_KEY=your_actual_finnhub_key_here
FMP_API_KEY=your_actual_fmp_key_here
PREFERRED_SOURCE=yfinance
CACHE_TIMEOUT=300
```

### Step 3: Use Configuration

```python
from market_data_fetcher import MarketDataFetcher
from config import get_config

# Load configuration from .env
config = get_config()

# Initialize fetcher with config
fetcher = MarketDataFetcher(
    finnhub_api_key=config.FINNHUB_API_KEY,
    fmp_api_key=config.FMP_API_KEY,
    preferred_source=config.PREFERRED_SOURCE
)
```

## 📖 API Reference

### MarketDataFetcher

#### `__init__(finnhub_api_key=None, fmp_api_key=None, preferred_source="yfinance", cache_timeout=300)`

Initialize the data fetcher.

**Parameters:**
- `finnhub_api_key` (str, optional): Finnhub API key
- `fmp_api_key` (str, optional): Financial Modeling Prep API key
- `preferred_source` (str): Preferred data source ("yfinance", "finnhub", or "fmp")
- `cache_timeout` (int): Cache timeout in seconds (default: 300)

#### `get_quote(symbol, source=None)`

Fetch current quote for a symbol.

**Parameters:**
- `symbol` (str): Stock ticker symbol (e.g., "AAPL")
- `source` (str, optional): Force specific source

**Returns:**
- `dict`: Quote data with price, volume, market cap, etc.

**Example:**
```python
quote = fetcher.get_quote("AAPL")
print(quote)
# {
#     'symbol': 'AAPL',
#     'price': 178.25,
#     'open': 177.50,
#     'high': 179.00,
#     'low': 176.80,
#     'volume': 52000000,
#     'market_cap': 2800000000000,
#     'pe_ratio': 28.5,
#     'source': 'yfinance'
# }
```

#### `get_historical(symbol, period="1y", interval="1d", source=None)`

Fetch historical price data.

**Parameters:**
- `symbol` (str): Stock ticker symbol
- `period` (str): Data period - "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"
- `interval` (str): Data interval - "1d", "1wk", "1mo"
- `source` (str, optional): Force specific source

**Returns:**
- `DataFrame`: Historical OHLCV data

**Example:**
```python
history = fetcher.get_historical("AAPL", period="3mo", interval="1d")
print(history.tail())
#                 Open    High     Low   Close    Volume
# 2025-02-10  177.50  179.00  176.80  178.25  52000000
# ...
```

#### `get_fundamentals(symbol, source=None)`

Fetch fundamental data.

**Parameters:**
- `symbol` (str): Stock ticker symbol
- `source` (str, optional): Force specific source

**Returns:**
- `dict`: Fundamental data (PE ratio, market cap, sector, etc.)

**Example:**
```python
fundamentals = fetcher.get_fundamentals("AAPL")
print(fundamentals)
# {
#     'company_name': 'Apple Inc.',
#     'sector': 'Technology',
#     'pe_ratio': 28.5,
#     'market_cap': 2800000000000,
#     'beta': 1.2,
#     ...
# }
```

#### `get_multiple_quotes(symbols)`

Fetch quotes for multiple symbols.

**Parameters:**
- `symbols` (list): List of stock ticker symbols

**Returns:**
- `DataFrame`: Quote data for all symbols

**Example:**
```python
symbols = ["AAPL", "MSFT", "GOOGL"]
quotes = fetcher.get_multiple_quotes(symbols)
print(quotes)
```

## 📝 Examples

### Example 1: Basic Stock Analysis

```python
from market_data_fetcher import MarketDataFetcher

fetcher = MarketDataFetcher()

# Get current data
quote = fetcher.get_quote("AAPL")
history = fetcher.get_historical("AAPL", period="1y")

# Calculate returns
returns = history['Close'].pct_change().dropna()
total_return = ((history['Close'].iloc[-1] / history['Close'].iloc[0]) - 1) * 100

print(f"Current Price: ${quote['price']:.2f}")
print(f"1Y Return: {total_return:.2f}%")
print(f"Volatility: {returns.std() * 100:.2f}%")
```

### Example 2: Portfolio Analysis

```python
from market_data_fetcher import MarketDataFetcher
import pandas as pd

fetcher = MarketDataFetcher()

# Portfolio of tech stocks
portfolio = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

# Fetch all quotes
quotes_df = fetcher.get_multiple_quotes(portfolio)

# Calculate portfolio metrics
total_market_cap = quotes_df['market_cap'].sum()
avg_pe = quotes_df['pe_ratio'].mean()

print(f"Total Market Cap: ${total_market_cap:,.0f}")
print(f"Average P/E: {avg_pe:.2f}")
```

### Example 3: Indian Stocks

```python
from market_data_fetcher import MarketDataFetcher

fetcher = MarketDataFetcher()

# Indian stocks require .NS suffix for NSE
indian_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]

for symbol in indian_stocks:
    quote = fetcher.get_quote(symbol)
    print(f"{symbol}: ₹{quote['price']:.2f}")
```

### Example 4: Mutual Funds & ETFs

```python
from market_data_fetcher import MarketDataFetcher

fetcher = MarketDataFetcher()

# Popular ETFs
etfs = ["SPY", "QQQ", "VOO", "VTI"]

for etf in etfs:
    quote = fetcher.get_quote(etf)
    history = fetcher.get_historical(etf, period="1y")
    ytd_return = ((history['Close'].iloc[-1] / history['Close'].iloc[0]) - 1) * 100

    print(f"{etf}: ${quote['price']:.2f} | YTD Return: {ytd_return:.2f}%")
```

## 🛠️ Integration with Mutual Fund Predictor

You can use this market data fetcher with the existing mutual fund profit predictor:

```python
from market_data_fetcher import MarketDataFetcher
import pandas as pd

# Initialize fetcher
fetcher = MarketDataFetcher()

# Fetch data for mutual funds / ETFs
symbols = ["SPY", "QQQ", "VOO", "VTI", "AGG"]

fund_data = []
for symbol in symbols:
    quote = fetcher.get_quote(symbol)
    history = fetcher.get_historical(symbol, period="1y")

    if history is not None:
        returns = history['Close'].pct_change().dropna()

        fund_data.append({
            'Name': symbol,
            'Price': quote['price'],
            'Volatility': returns.std() * 100,
            'Absolute Returns - 1Y': ((history['Close'].iloc[-1] /
                                       history['Close'].iloc[0]) - 1) * 100,
            'Sharpe Ratio': (returns.mean() / returns.std()) * np.sqrt(252),
            'AUM': quote.get('market_cap', 0) / 10000000  # Convert to Cr
        })

# Create DataFrame for analysis
df = pd.DataFrame(fund_data)

# Now you can use this with the profit predictor
# from mutual_fund_profit_predictor import maximize_profits
# results, recommendations = maximize_profits(df)
```

## 🔧 Troubleshooting

### yfinance Getting Blocked

**Problem**: `429 Too Many Requests` error

**Solutions**:
1. Use API keys for Finnhub or FMP (automatic fallback)
2. Reduce request frequency
3. Use caching more aggressively
4. Add delays between requests

```python
# Configure for aggressive rate limiting
fetcher = MarketDataFetcher(
    finnhub_api_key="your_key",
    cache_timeout=600  # 10 minutes
)
```

### Rate Limit Exceeded

**Problem**: All sources returning rate limit errors

**Solutions**:
1. Increase cache timeout
2. Batch requests with delays
3. Upgrade to paid API plans

```python
import time

# Add delay between requests
for symbol in symbols:
    quote = fetcher.get_quote(symbol)
    time.sleep(1)  # 1 second delay
```

### Invalid Symbol

**Problem**: No data returned for symbol

**Solutions**:
1. Check symbol format (use `.NS` for Indian stocks, `.L` for London, etc.)
2. Verify symbol is correct on Yahoo Finance
3. Try different data source

```python
# Try multiple sources
quote = fetcher.get_quote("AAPL", source="yfinance")
if not quote:
    quote = fetcher.get_quote("AAPL", source="finnhub")
```

## 📊 Performance Tips

1. **Use Caching**: Default 5-minute cache reduces API calls significantly
2. **Batch Requests**: Use `get_multiple_quotes()` instead of loops
3. **Choose Right Source**:
   - yfinance: Best for historical data
   - Finnhub: Best for real-time quotes
   - FMP: Best for fundamentals
4. **Monitor Rate Limits**: Check source documentation for limits

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API wrapper
- [Finnhub](https://finnhub.io/) - Real-time stock API
- [Financial Modeling Prep](https://financialmodelingprep.com/) - Financial data API

## 📞 Support

For issues and questions:
- Check the [examples](example_usage.py)
- Review the [troubleshooting guide](#troubleshooting)
- Open an issue on GitHub

---

**Made with ❤️ for data-driven investors**

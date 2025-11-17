"""
Example Usage - Market Data Fetcher
====================================

Demonstrates how to use the MarketDataFetcher with all three data sources:
1. Yahoo Finance (yfinance)
2. Finnhub
3. Financial Modeling Prep (FMP)
"""

from market_data_fetcher import MarketDataFetcher, create_fetcher
import pandas as pd

# Set display options for better output
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', '{:.2f}'.format)


def example_1_basic_usage():
    """Example 1: Basic usage with yfinance only (no API keys needed)"""

    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Usage with yfinance (No API Keys Needed)")
    print("="*80)

    # Create fetcher with yfinance only
    fetcher = create_fetcher(yfinance_only=True)

    # Fetch quote
    print("\n1. Fetching Quote for AAPL:")
    print("-" * 60)
    quote = fetcher.get_quote("AAPL")
    if quote:
        print(f"Symbol: {quote['symbol']}")
        print(f"Price: ${quote.get('price', 'N/A'):.2f}")
        print(f"Open: ${quote.get('open', 'N/A'):.2f}")
        print(f"High: ${quote.get('high', 'N/A'):.2f}")
        print(f"Low: ${quote.get('low', 'N/A'):.2f}")
        print(f"Volume: {quote.get('volume', 'N/A'):,}")
        print(f"Market Cap: ${quote.get('market_cap', 0):,.0f}")
        print(f"P/E Ratio: {quote.get('pe_ratio', 'N/A')}")
        print(f"Source: {quote['source']}")

    # Fetch historical data
    print("\n2. Fetching Historical Data (Last 3 Months):")
    print("-" * 60)
    history = fetcher.get_historical("AAPL", period="3mo", interval="1d")
    if history is not None:
        print(f"Retrieved {len(history)} days of data")
        print("\nLast 5 days:")
        print(history.tail())

        # Calculate returns
        returns = history['Close'].pct_change().dropna()
        print(f"\nAverage Daily Return: {returns.mean()*100:.2f}%")
        print(f"Volatility (Std Dev): {returns.std()*100:.2f}%")
        print(f"Total Return: {((history['Close'].iloc[-1] / history['Close'].iloc[0]) - 1) * 100:.2f}%")

    # Fetch fundamentals
    print("\n3. Fetching Fundamental Data:")
    print("-" * 60)
    fundamentals = fetcher.get_fundamentals("AAPL")
    if fundamentals:
        print(f"Company: {fundamentals.get('company_name', 'N/A')}")
        print(f"Sector: {fundamentals.get('sector', 'N/A')}")
        print(f"Industry: {fundamentals.get('industry', 'N/A')}")
        print(f"Market Cap: ${fundamentals.get('market_cap', 0):,.0f}")
        print(f"P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}")
        print(f"Forward P/E: {fundamentals.get('forward_pe', 'N/A')}")
        print(f"Price/Book: {fundamentals.get('price_to_book', 'N/A')}")
        print(f"Beta: {fundamentals.get('beta', 'N/A')}")
        print(f"Dividend Yield: {fundamentals.get('dividend_yield', 'N/A')}")
        print(f"Source: {fundamentals['source']}")


def example_2_multiple_sources():
    """Example 2: Using multiple data sources with API keys"""

    print("\n" + "="*80)
    print("EXAMPLE 2: Using Multiple Data Sources with Fallback")
    print("="*80)

    # IMPORTANT: Replace with your actual API keys
    FINNHUB_API_KEY = "your_finnhub_api_key_here"
    FMP_API_KEY = "your_fmp_api_key_here"

    # Create fetcher with all sources
    # Note: Will fallback to yfinance if API keys are not provided
    fetcher = MarketDataFetcher(
        finnhub_api_key=FINNHUB_API_KEY if FINNHUB_API_KEY != "your_finnhub_api_key_here" else None,
        fmp_api_key=FMP_API_KEY if FMP_API_KEY != "your_fmp_api_key_here" else None,
        preferred_source="yfinance"
    )

    print(f"\nAvailable sources: {fetcher.source_priority}")

    # Fetch from preferred source (with automatic fallback)
    print("\n1. Fetching with Automatic Fallback:")
    print("-" * 60)
    quote = fetcher.get_quote("MSFT")
    if quote:
        print(f"✅ Got quote from: {quote['source']}")
        print(f"Price: ${quote.get('price', 'N/A'):.2f}")

    # Force specific source
    print("\n2. Forcing Specific Source (yfinance):")
    print("-" * 60)
    quote_yf = fetcher.get_quote("GOOGL", source="yfinance")
    if quote_yf:
        print(f"✅ Got quote from: {quote_yf['source']}")
        print(f"Price: ${quote_yf.get('price', 'N/A'):.2f}")


def example_3_multiple_symbols():
    """Example 3: Fetching data for multiple symbols"""

    print("\n" + "="*80)
    print("EXAMPLE 3: Fetching Multiple Symbols")
    print("="*80)

    fetcher = create_fetcher(yfinance_only=True)

    # Popular tech stocks
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"]

    print(f"\nFetching quotes for: {', '.join(symbols)}")
    print("-" * 60)

    quotes_df = fetcher.get_multiple_quotes(symbols)

    if not quotes_df.empty:
        print("\nQuotes retrieved successfully:")
        print(quotes_df[['symbol', 'price', 'change_percent', 'volume', 'market_cap', 'pe_ratio']].to_string(index=False))

        # Calculate portfolio metrics
        print("\n📊 Portfolio Summary:")
        total_market_cap = quotes_df['market_cap'].sum()
        avg_pe = quotes_df['pe_ratio'].mean()
        print(f"Total Market Cap: ${total_market_cap:,.0f}")
        print(f"Average P/E Ratio: {avg_pe:.2f}")


def example_4_indian_stocks():
    """Example 4: Fetching Indian stock data"""

    print("\n" + "="*80)
    print("EXAMPLE 4: Fetching Indian Stock Data")
    print("="*80)

    fetcher = create_fetcher(yfinance_only=True)

    # Indian stocks (NSE symbols need .NS suffix for yfinance)
    indian_symbols = {
        "RELIANCE.NS": "Reliance Industries",
        "TCS.NS": "Tata Consultancy Services",
        "HDFCBANK.NS": "HDFC Bank",
        "INFY.NS": "Infosys",
        "ICICIBANK.NS": "ICICI Bank"
    }

    print("\nFetching quotes for top Indian stocks:")
    print("-" * 60)

    for symbol, name in indian_symbols.items():
        quote = fetcher.get_quote(symbol)
        if quote:
            print(f"\n{name} ({symbol}):")
            print(f"  Price: ₹{quote.get('price', 'N/A'):.2f}")
            print(f"  P/E Ratio: {quote.get('pe_ratio', 'N/A')}")
            print(f"  Market Cap: ₹{quote.get('market_cap', 0):,.0f}")


def example_5_mutual_funds():
    """Example 5: Fetching mutual fund data"""

    print("\n" + "="*80)
    print("EXAMPLE 5: Fetching Mutual Fund Data")
    print("="*80)

    fetcher = create_fetcher(yfinance_only=True)

    # Popular US mutual funds and ETFs
    funds = {
        "SPY": "S&P 500 ETF",
        "QQQ": "Nasdaq-100 ETF",
        "VOO": "Vanguard S&P 500 ETF",
        "VTI": "Vanguard Total Stock Market ETF",
        "AGG": "iShares Core US Aggregate Bond ETF"
    }

    print("\nFetching fund data:")
    print("-" * 60)

    fund_data = []

    for symbol, name in funds.items():
        quote = fetcher.get_quote(symbol)
        if quote:
            # Get historical data to calculate returns
            hist = fetcher.get_historical(symbol, period="1y", interval="1d")

            if hist is not None and len(hist) > 0:
                year_return = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                volatility = hist['Close'].pct_change().std() * 100

                fund_data.append({
                    'Symbol': symbol,
                    'Name': name,
                    'Price': quote.get('price', 0),
                    'YTD Return (%)': year_return,
                    'Volatility (%)': volatility,
                    'Volume': quote.get('volume', 0)
                })

    if fund_data:
        df = pd.DataFrame(fund_data)
        print("\nFund Performance Summary:")
        print(df.to_string(index=False))


def example_6_cache_management():
    """Example 6: Cache management"""

    print("\n" + "="*80)
    print("EXAMPLE 6: Cache Management")
    print("="*80)

    fetcher = create_fetcher(yfinance_only=True)

    # First fetch - will hit API
    print("\n1. First fetch (will hit API):")
    fetcher.get_quote("AAPL")

    # Second fetch - will use cache
    print("\n2. Second fetch (will use cache):")
    fetcher.get_quote("AAPL")

    # Check cache stats
    print("\n3. Cache Statistics:")
    stats = fetcher.get_cache_stats()
    print(f"Total cached entries: {stats['total_entries']}")
    print(f"Cache timeout: {stats['cache_timeout']} seconds")
    print(f"Cached keys: {stats['entries']}")

    # Clear cache
    print("\n4. Clearing cache:")
    fetcher.clear_cache()

    stats = fetcher.get_cache_stats()
    print(f"Total cached entries after clear: {stats['total_entries']}")


def example_7_error_handling():
    """Example 7: Error handling and fallback"""

    print("\n" + "="*80)
    print("EXAMPLE 7: Error Handling and Fallback")
    print("="*80)

    fetcher = create_fetcher(yfinance_only=True)

    # Try fetching invalid symbol
    print("\n1. Fetching invalid symbol:")
    quote = fetcher.get_quote("INVALID_SYMBOL_XYZ")
    if quote is None:
        print("✅ Correctly handled invalid symbol")

    # Try fetching with all sources (will fallback)
    print("\n2. Testing fallback mechanism:")
    fetcher_multi = MarketDataFetcher(
        finnhub_api_key=None,  # Invalid key
        fmp_api_key=None,  # Invalid key
        preferred_source="finnhub"  # Will fallback to yfinance
    )

    quote = fetcher_multi.get_quote("AAPL")
    if quote:
        print(f"✅ Successfully fell back to: {quote['source']}")


def example_8_advanced_analysis():
    """Example 8: Advanced analysis combining multiple data points"""

    print("\n" + "="*80)
    print("EXAMPLE 8: Advanced Multi-Stock Analysis")
    print("="*80)

    fetcher = create_fetcher(yfinance_only=True)

    # Tech stocks for comparison
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

    print(f"\nAnalyzing: {', '.join(symbols)}")
    print("-" * 60)

    analysis_data = []

    for symbol in symbols:
        # Get quote
        quote = fetcher.get_quote(symbol)

        # Get historical data
        hist = fetcher.get_historical(symbol, period="1y", interval="1d")

        # Get fundamentals
        fundamentals = fetcher.get_fundamentals(symbol)

        if quote and hist is not None and fundamentals:
            returns = hist['Close'].pct_change().dropna()

            analysis_data.append({
                'Symbol': symbol,
                'Company': fundamentals.get('company_name', 'N/A'),
                'Price': quote.get('price', 0),
                'Market Cap (B)': quote.get('market_cap', 0) / 1e9,
                'P/E Ratio': quote.get('pe_ratio', 0),
                '1Y Return (%)': ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100,
                'Volatility (%)': returns.std() * 100,
                'Sharpe Ratio': (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0,
                'Beta': fundamentals.get('beta', 0)
            })

    if analysis_data:
        import numpy as np
        df = pd.DataFrame(analysis_data)

        print("\n📊 Comprehensive Analysis:")
        print(df.to_string(index=False))

        print("\n🏆 Best Performers:")
        print(f"Highest Return: {df.loc[df['1Y Return (%)'].idxmax(), 'Symbol']} ({df['1Y Return (%)'].max():.2f}%)")
        print(f"Best Sharpe Ratio: {df.loc[df['Sharpe Ratio'].idxmax(), 'Symbol']} ({df['Sharpe Ratio'].max():.2f})")
        print(f"Lowest Volatility: {df.loc[df['Volatility (%)'].idxmin(), 'Symbol']} ({df['Volatility (%)'].min():.2f}%)")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║          📊 MARKET DATA FETCHER - EXAMPLE USAGE                      ║
║                                                                      ║
║  This script demonstrates all features of the MarketDataFetcher     ║
║  including multiple data sources, caching, and error handling.      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    import numpy as np

    try:
        # Run all examples
        example_1_basic_usage()
        example_2_multiple_sources()
        example_3_multiple_symbols()
        example_4_indian_stocks()
        example_5_mutual_funds()
        example_6_cache_management()
        example_7_error_handling()
        example_8_advanced_analysis()

        print("\n" + "="*80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nNote: Make sure you have the required packages installed:")
        print("  pip install yfinance finnhub-python requests pandas numpy")

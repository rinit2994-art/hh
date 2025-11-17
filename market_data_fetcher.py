"""
Market Data Fetcher - Multi-Source Data Agent
==============================================

Unified interface for fetching market data from multiple sources:
- Yahoo Finance (yfinance) - Free, but rate-limited
- Finnhub - Free tier: 60 calls/min
- Financial Modeling Prep (FMP) - Free tier: 250 calls/day

Features:
- Automatic fallback between sources
- Rate limiting with exponential backoff
- Retry logic for network failures
- Caching to reduce API calls
- Unified data format across all sources

Usage:
------
from market_data_fetcher import MarketDataFetcher

# Initialize with API keys (optional for yfinance)
fetcher = MarketDataFetcher(
    finnhub_api_key="your_finnhub_key",
    fmp_api_key="your_fmp_key"
)

# Fetch quote data
quote = fetcher.get_quote("AAPL")

# Fetch historical data
history = fetcher.get_historical("AAPL", period="1y")

# Fetch fundamentals
fundamentals = fetcher.get_fundamentals("AAPL")
"""

import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union, Tuple
import warnings
warnings.filterwarnings('ignore')

# Optional imports with graceful fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance not installed. Install with: pip install yfinance")

try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False
    print("⚠️ finnhub-python not installed. Install with: pip install finnhub-python")


class RateLimiter:
    """Simple rate limiter with exponential backoff"""

    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0

    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()


class MarketDataFetcher:
    """
    Unified market data fetcher with multiple sources and automatic fallback
    """

    def __init__(
        self,
        finnhub_api_key: Optional[str] = None,
        fmp_api_key: Optional[str] = None,
        preferred_source: str = "yfinance",
        cache_timeout: int = 300  # 5 minutes
    ):
        """
        Initialize the market data fetcher

        Parameters:
        -----------
        finnhub_api_key : str, optional
            Finnhub API key for real-time data
        fmp_api_key : str, optional
            Financial Modeling Prep API key
        preferred_source : str
            Preferred data source: "yfinance", "finnhub", or "fmp"
        cache_timeout : int
            Cache timeout in seconds (default: 300)
        """
        self.finnhub_api_key = finnhub_api_key
        self.fmp_api_key = fmp_api_key
        self.preferred_source = preferred_source
        self.cache = {}
        self.cache_timeout = cache_timeout

        # Initialize clients
        self.finnhub_client = None
        if FINNHUB_AVAILABLE and finnhub_api_key:
            try:
                self.finnhub_client = finnhub.Client(api_key=finnhub_api_key)
                print("✅ Finnhub client initialized")
            except Exception as e:
                print(f"⚠️ Finnhub initialization failed: {e}")

        # Rate limiters for each source
        self.rate_limiters = {
            'yfinance': RateLimiter(calls_per_minute=60),  # Conservative
            'finnhub': RateLimiter(calls_per_minute=60),
            'fmp': RateLimiter(calls_per_minute=250)  # Daily limit, but being conservative
        }

        # Source priority order
        self.source_priority = self._get_source_priority()

        print(f"🚀 MarketDataFetcher initialized")
        print(f"   Preferred source: {preferred_source}")
        print(f"   Available sources: {', '.join(self.source_priority)}")

    def _get_source_priority(self) -> List[str]:
        """Determine source priority based on availability and preference"""
        available = []

        if self.preferred_source == "yfinance" and YFINANCE_AVAILABLE:
            available.append("yfinance")

        if self.finnhub_client:
            available.append("finnhub")

        if self.fmp_api_key:
            available.append("fmp")

        # Add yfinance as fallback if not preferred but available
        if "yfinance" not in available and YFINANCE_AVAILABLE:
            available.append("yfinance")

        return available if available else ["yfinance"]  # Default fallback

    def _get_cache_key(self, operation: str, symbol: str, **kwargs) -> str:
        """Generate cache key for operation"""
        params = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{operation}_{symbol}_{params}"

    def _check_cache(self, key: str) -> Optional[any]:
        """Check if cached data is still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_timeout:
                return data
        return None

    def _update_cache(self, key: str, data: any):
        """Update cache with new data"""
        self.cache[key] = (data, time.time())

    def _retry_with_backoff(
        self,
        func,
        max_retries: int = 4,
        initial_delay: float = 2.0
    ) -> Tuple[any, bool]:
        """
        Retry function with exponential backoff

        Returns:
        --------
        (result, success) : tuple
            Result of function call and success status
        """
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                result = func()
                return result, True
            except Exception as e:
                error_str = str(e).lower()

                # Check if it's a rate limit error
                if '429' in error_str or 'rate limit' in error_str or 'too many requests' in error_str:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Rate limited, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                        continue
                    else:
                        print(f"❌ Rate limit exceeded after {max_retries} attempts")
                        return None, False

                # For other errors, fail fast
                print(f"❌ Error: {e}")
                return None, False

        return None, False

    # ==================== YFINANCE METHODS ====================

    def _yfinance_get_quote(self, symbol: str) -> Optional[Dict]:
        """Fetch quote using yfinance"""
        if not YFINANCE_AVAILABLE:
            return None

        self.rate_limiters['yfinance'].wait_if_needed()

        def fetch():
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'previous_close': info.get('previousClose'),
                'open': info.get('open') or info.get('regularMarketOpen'),
                'high': info.get('dayHigh') or info.get('regularMarketDayHigh'),
                'low': info.get('dayLow') or info.get('regularMarketDayLow'),
                'volume': info.get('volume') or info.get('regularMarketVolume'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'dividend_yield': info.get('dividendYield'),
                'source': 'yfinance'
            }

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    def _yfinance_get_historical(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data using yfinance"""
        if not YFINANCE_AVAILABLE:
            return None

        self.rate_limiters['yfinance'].wait_if_needed()

        def fetch():
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            df['source'] = 'yfinance'
            return df

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    def _yfinance_get_fundamentals(self, symbol: str) -> Optional[Dict]:
        """Fetch fundamental data using yfinance"""
        if not YFINANCE_AVAILABLE:
            return None

        self.rate_limiters['yfinance'].wait_if_needed()

        def fetch():
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'company_name': info.get('longName') or info.get('shortName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'revenue': info.get('totalRevenue'),
                'profit_margin': info.get('profitMargins'),
                'beta': info.get('beta'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'source': 'yfinance'
            }

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    # ==================== FINNHUB METHODS ====================

    def _finnhub_get_quote(self, symbol: str) -> Optional[Dict]:
        """Fetch quote using Finnhub"""
        if not self.finnhub_client:
            return None

        self.rate_limiters['finnhub'].wait_if_needed()

        def fetch():
            quote = self.finnhub_client.quote(symbol)

            return {
                'symbol': symbol,
                'price': quote.get('c'),  # Current price
                'previous_close': quote.get('pc'),
                'open': quote.get('o'),
                'high': quote.get('h'),
                'low': quote.get('l'),
                'change': quote.get('d'),
                'change_percent': quote.get('dp'),
                'source': 'finnhub'
            }

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    def _finnhub_get_historical(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data using Finnhub"""
        if not self.finnhub_client:
            return None

        self.rate_limiters['finnhub'].wait_if_needed()

        # Convert period to timestamps
        end_time = int(datetime.now().timestamp())

        period_map = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
            '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
        }
        days = period_map.get(period, 365)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())

        # Finnhub resolution
        resolution_map = {'1d': 'D', '1wk': 'W', '1mo': 'M'}
        resolution = resolution_map.get(interval, 'D')

        def fetch():
            data = self.finnhub_client.stock_candles(
                symbol, resolution, start_time, end_time
            )

            if data.get('s') != 'ok':
                raise ValueError(f"Finnhub returned status: {data.get('s')}")

            df = pd.DataFrame({
                'Open': data['o'],
                'High': data['h'],
                'Low': data['l'],
                'Close': data['c'],
                'Volume': data['v']
            }, index=pd.to_datetime(data['t'], unit='s'))

            df['source'] = 'finnhub'
            return df

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    def _finnhub_get_fundamentals(self, symbol: str) -> Optional[Dict]:
        """Fetch fundamental data using Finnhub"""
        if not self.finnhub_client:
            return None

        self.rate_limiters['finnhub'].wait_if_needed()

        def fetch():
            # Get company profile
            profile = self.finnhub_client.company_profile2(symbol=symbol)

            # Get basic financials
            try:
                metrics = self.finnhub_client.company_basic_financials(symbol, 'all')
                metric_data = metrics.get('metric', {})
            except:
                metric_data = {}

            return {
                'symbol': symbol,
                'company_name': profile.get('name'),
                'sector': profile.get('finnhubIndustry'),
                'market_cap': profile.get('marketCapitalization'),
                'pe_ratio': metric_data.get('peBasicExclExtraTTM'),
                'price_to_book': metric_data.get('pbQuarterly'),
                'dividend_yield': metric_data.get('dividendYieldIndicatedAnnual'),
                'beta': metric_data.get('beta'),
                'fifty_two_week_high': metric_data.get('52WeekHigh'),
                'fifty_two_week_low': metric_data.get('52WeekLow'),
                'source': 'finnhub'
            }

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    # ==================== FMP METHODS ====================

    def _fmp_get_quote(self, symbol: str) -> Optional[Dict]:
        """Fetch quote using Financial Modeling Prep"""
        if not self.fmp_api_key:
            return None

        self.rate_limiters['fmp'].wait_if_needed()

        def fetch():
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}"
            response = requests.get(url, params={'apikey': self.fmp_api_key})
            response.raise_for_status()

            data = response.json()
            if not data:
                raise ValueError(f"No data returned for {symbol}")

            quote = data[0]

            return {
                'symbol': symbol,
                'price': quote.get('price'),
                'previous_close': quote.get('previousClose'),
                'open': quote.get('open'),
                'high': quote.get('dayHigh'),
                'low': quote.get('dayLow'),
                'volume': quote.get('volume'),
                'market_cap': quote.get('marketCap'),
                'pe_ratio': quote.get('pe'),
                'change': quote.get('change'),
                'change_percent': quote.get('changesPercentage'),
                'source': 'fmp'
            }

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    def _fmp_get_historical(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data using FMP"""
        if not self.fmp_api_key:
            return None

        self.rate_limiters['fmp'].wait_if_needed()

        def fetch():
            url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}"

            # FMP doesn't have great period support, so we fetch and filter
            response = requests.get(url, params={'apikey': self.fmp_api_key})
            response.raise_for_status()

            data = response.json()

            if 'historical' not in data:
                raise ValueError(f"No historical data for {symbol}")

            df = pd.DataFrame(data['historical'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()

            # Filter by period
            period_map = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
                '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
            }
            days = period_map.get(period, 365)
            cutoff = datetime.now() - timedelta(days=days)
            df = df[df.index >= cutoff]

            # Rename columns to match yfinance format
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })

            df['source'] = 'fmp'
            return df[['Open', 'High', 'Low', 'Close', 'Volume', 'source']]

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    def _fmp_get_fundamentals(self, symbol: str) -> Optional[Dict]:
        """Fetch fundamental data using FMP"""
        if not self.fmp_api_key:
            return None

        self.rate_limiters['fmp'].wait_if_needed()

        def fetch():
            # Get company profile
            url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}"
            response = requests.get(url, params={'apikey': self.fmp_api_key})
            response.raise_for_status()

            data = response.json()
            if not data:
                raise ValueError(f"No profile data for {symbol}")

            profile = data[0]

            return {
                'symbol': symbol,
                'company_name': profile.get('companyName'),
                'sector': profile.get('sector'),
                'industry': profile.get('industry'),
                'market_cap': profile.get('mktCap'),
                'pe_ratio': profile.get('pe'),
                'price_to_book': profile.get('priceToBook'),
                'dividend_yield': profile.get('lastDiv'),
                'beta': profile.get('beta'),
                'fifty_two_week_high': profile.get('range'),  # Comes as string
                'fifty_two_week_low': profile.get('range'),
                'description': profile.get('description'),
                'website': profile.get('website'),
                'ceo': profile.get('ceo'),
                'source': 'fmp'
            }

        result, success = self._retry_with_backoff(fetch)
        return result if success else None

    # ==================== PUBLIC API METHODS ====================

    def get_quote(self, symbol: str, source: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch current quote for a symbol

        Parameters:
        -----------
        symbol : str
            Stock ticker symbol
        source : str, optional
            Specific source to use (overrides preference)

        Returns:
        --------
        dict : Quote data with price, volume, etc.
        """
        cache_key = self._get_cache_key('quote', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        sources_to_try = [source] if source else self.source_priority

        for src in sources_to_try:
            print(f"📊 Fetching quote for {symbol} from {src}...")

            if src == 'yfinance':
                result = self._yfinance_get_quote(symbol)
            elif src == 'finnhub':
                result = self._finnhub_get_quote(symbol)
            elif src == 'fmp':
                result = self._fmp_get_quote(symbol)
            else:
                continue

            if result:
                self._update_cache(cache_key, result)
                print(f"✅ Quote fetched successfully from {src}")
                return result
            else:
                print(f"⚠️ Failed to fetch from {src}, trying next source...")

        print(f"❌ Failed to fetch quote for {symbol} from all sources")
        return None

    def get_historical(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        source: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data

        Parameters:
        -----------
        symbol : str
            Stock ticker symbol
        period : str
            Data period: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"
        interval : str
            Data interval: "1d", "1wk", "1mo"
        source : str, optional
            Specific source to use

        Returns:
        --------
        DataFrame : Historical OHLCV data
        """
        cache_key = self._get_cache_key('historical', symbol, period=period, interval=interval)
        cached = self._check_cache(cache_key)
        if cached is not None:
            return cached

        sources_to_try = [source] if source else self.source_priority

        for src in sources_to_try:
            print(f"📈 Fetching historical data for {symbol} from {src}...")

            if src == 'yfinance':
                result = self._yfinance_get_historical(symbol, period, interval)
            elif src == 'finnhub':
                result = self._finnhub_get_historical(symbol, period, interval)
            elif src == 'fmp':
                result = self._fmp_get_historical(symbol, period, interval)
            else:
                continue

            if result is not None and not result.empty:
                self._update_cache(cache_key, result)
                print(f"✅ Historical data fetched successfully from {src}")
                return result
            else:
                print(f"⚠️ Failed to fetch from {src}, trying next source...")

        print(f"❌ Failed to fetch historical data for {symbol} from all sources")
        return None

    def get_fundamentals(self, symbol: str, source: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch fundamental data for a symbol

        Parameters:
        -----------
        symbol : str
            Stock ticker symbol
        source : str, optional
            Specific source to use

        Returns:
        --------
        dict : Fundamental data (PE, market cap, sector, etc.)
        """
        cache_key = self._get_cache_key('fundamentals', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        sources_to_try = [source] if source else self.source_priority

        for src in sources_to_try:
            print(f"📊 Fetching fundamentals for {symbol} from {src}...")

            if src == 'yfinance':
                result = self._yfinance_get_fundamentals(symbol)
            elif src == 'finnhub':
                result = self._finnhub_get_fundamentals(symbol)
            elif src == 'fmp':
                result = self._fmp_get_fundamentals(symbol)
            else:
                continue

            if result:
                self._update_cache(cache_key, result)
                print(f"✅ Fundamentals fetched successfully from {src}")
                return result
            else:
                print(f"⚠️ Failed to fetch from {src}, trying next source...")

        print(f"❌ Failed to fetch fundamentals for {symbol} from all sources")
        return None

    def get_multiple_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """
        Fetch quotes for multiple symbols

        Parameters:
        -----------
        symbols : list
            List of stock ticker symbols

        Returns:
        --------
        DataFrame : Quote data for all symbols
        """
        quotes = []

        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                quotes.append(quote)
            time.sleep(0.5)  # Small delay between requests

        return pd.DataFrame(quotes)

    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}
        print("🗑️ Cache cleared")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'cache_timeout': self.cache_timeout,
            'entries': list(self.cache.keys())
        }


# ==================== CONVENIENCE FUNCTIONS ====================

def create_fetcher(
    yfinance_only: bool = False,
    finnhub_key: Optional[str] = None,
    fmp_key: Optional[str] = None
) -> MarketDataFetcher:
    """
    Quick fetcher creation

    Parameters:
    -----------
    yfinance_only : bool
        Use only yfinance (no API keys needed)
    finnhub_key : str, optional
        Finnhub API key
    fmp_key : str, optional
        FMP API key

    Returns:
    --------
    MarketDataFetcher : Initialized fetcher
    """
    if yfinance_only:
        return MarketDataFetcher(preferred_source="yfinance")
    else:
        return MarketDataFetcher(
            finnhub_api_key=finnhub_key,
            fmp_api_key=fmp_key,
            preferred_source="yfinance"
        )


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║          📊 MARKET DATA FETCHER - MULTI-SOURCE AGENT         ║
║                                                              ║
║  Supports:                                                   ║
║  ✅ Yahoo Finance (yfinance) - Free, rate-limited           ║
║  ✅ Finnhub - 60 calls/min free tier                        ║
║  ✅ Financial Modeling Prep - 250 calls/day free tier       ║
║                                                              ║
║  Features:                                                   ║
║  • Automatic fallback between sources                       ║
║  • Rate limiting with exponential backoff                   ║
║  • Built-in caching                                          ║
║  • Unified data format                                       ║
╚══════════════════════════════════════════════════════════════╝
    """)

    print("\nExample usage:")
    print("-" * 60)
    print("from market_data_fetcher import MarketDataFetcher")
    print("")
    print("# Initialize (yfinance only, no API keys needed)")
    print("fetcher = MarketDataFetcher()")
    print("")
    print("# Fetch quote")
    print("quote = fetcher.get_quote('AAPL')")
    print("")
    print("# Fetch historical data")
    print("history = fetcher.get_historical('AAPL', period='1y')")
    print("")
    print("# Fetch fundamentals")
    print("fundamentals = fetcher.get_fundamentals('AAPL')")

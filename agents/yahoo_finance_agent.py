"""Yahoo Finance Agent - Fetches financial data from Yahoo Finance."""

from google.adk.agents import LlmAgent
from typing import Dict, List, Any
import requests
import json
from datetime import datetime, timedelta


def fetch_stock_quote(symbol: str) -> Dict[str, Any]:
    """
    Fetch current stock quote for a given symbol from Yahoo Finance.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary containing current stock price and related information
    """
    try:
        # Yahoo Finance API endpoint
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "interval": "1d",
            "range": "5d"
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'chart' not in data or 'result' not in data['chart']:
            return {"error": f"No data found for symbol {symbol}"}

        result = data['chart']['result'][0]
        meta = result.get('meta', {})

        return {
            "symbol": symbol,
            "current_price": meta.get('regularMarketPrice'),
            "previous_close": meta.get('previousClose'),
            "currency": meta.get('currency'),
            "exchange": meta.get('exchangeName'),
            "timestamp": datetime.fromtimestamp(meta.get('regularMarketTime', 0)).isoformat()
        }
    except Exception as e:
        return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}


def fetch_stock_history(symbol: str, period: str = "1mo") -> Dict[str, Any]:
    """
    Fetch historical stock data for a given symbol.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        Dictionary containing historical price data
    """
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "interval": "1d",
            "range": period
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'chart' not in data or 'result' not in data['chart']:
            return {"error": f"No data found for symbol {symbol}"}

        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]

        history = []
        for i, ts in enumerate(timestamps):
            history.append({
                "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                "open": quotes['open'][i],
                "high": quotes['high'][i],
                "low": quotes['low'][i],
                "close": quotes['close'][i],
                "volume": quotes['volume'][i]
            })

        return {
            "symbol": symbol,
            "period": period,
            "data_points": len(history),
            "history": history
        }
    except Exception as e:
        return {"error": f"Failed to fetch historical data for {symbol}: {str(e)}"}


def search_ticker_symbol(company_name: str) -> Dict[str, Any]:
    """
    Search for ticker symbol by company name.

    Args:
        company_name: Name of the company

    Returns:
        Dictionary containing potential ticker symbols
    """
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {
            "q": company_name,
            "quotesCount": 5,
            "newsCount": 0
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        quotes = data.get('quotes', [])

        results = []
        for quote in quotes[:5]:
            results.append({
                "symbol": quote.get('symbol'),
                "name": quote.get('shortname') or quote.get('longname'),
                "exchange": quote.get('exchange'),
                "type": quote.get('quoteType')
            })

        return {
            "query": company_name,
            "results": results
        }
    except Exception as e:
        return {"error": f"Failed to search for {company_name}: {str(e)}"}


def get_mutual_fund_info(symbol: str) -> Dict[str, Any]:
    """
    Get mutual fund information including NAV, performance, and holdings.

    Args:
        symbol: Mutual fund ticker symbol

    Returns:
        Dictionary containing mutual fund information
    """
    try:
        # Get basic quote data
        quote_data = fetch_stock_quote(symbol)

        # Get additional fund information
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
        params = {
            "modules": "summaryDetail,fundProfile,defaultKeyStatistics"
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        result = data.get('quoteSummary', {}).get('result', [{}])[0]

        summary = result.get('summaryDetail', {})
        profile = result.get('fundProfile', {})
        key_stats = result.get('defaultKeyStatistics', {})

        return {
            "symbol": symbol,
            "nav": summary.get('navPrice', {}).get('raw'),
            "previous_close": summary.get('previousClose', {}).get('raw'),
            "ytd_return": summary.get('ytdReturn', {}).get('raw'),
            "category": profile.get('categoryName'),
            "family": profile.get('family'),
            "inception_date": key_stats.get('fundInceptionDate', {}).get('fmt'),
            **quote_data
        }
    except Exception as e:
        return {"error": f"Failed to fetch mutual fund info for {symbol}: {str(e)}"}


# Create the Yahoo Finance agent
yahoo_finance_agent = LlmAgent(
    name="yahoo_finance_agent",
    model="gemini-2.0-flash-exp",
    description="I fetch real-time and historical financial data from Yahoo Finance, including stock quotes, mutual fund information, and ticker symbols.",
    instruction="""You are a Yahoo Finance data specialist. Your role is to:

    1. Fetch current stock quotes and prices
    2. Retrieve historical stock data for analysis
    3. Search for ticker symbols by company name
    4. Get mutual fund information including NAV and performance

    Always provide accurate financial data and handle errors gracefully.
    When presenting data, include relevant context like timestamps and currency.
    """,
    tools=[
        fetch_stock_quote,
        fetch_stock_history,
        search_ticker_symbol,
        get_mutual_fund_info
    ]
)

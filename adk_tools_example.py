#!/usr/bin/env python3
"""
ADK Tools Example - Demonstrating 4 Essential Tools
====================================================
1. Yahoo Finance Tool (custom)
2. Google Search Tool (built-in)
3. Code Execution Tool (built-in)
4. CSV File Data Tool (custom)
"""

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from google.generativeai import genai_adk_dev as adk

# Set up Google AI API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your-api-key-here")


# ============================================================================
# TOOL 1: Yahoo Finance Tool (Custom)
# ============================================================================
def get_stock_data(ticker: str, period: str = "1mo") -> dict:
    """
    Fetch stock data from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '5y')

    Returns:
        Dictionary containing stock data including price, change, volume, etc.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period=period)

        if hist.empty:
            return {"error": f"No data found for ticker {ticker}"}

        current_price = hist['Close'].iloc[-1]
        previous_price = hist['Close'].iloc[0]
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100

        return {
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": int(hist['Volume'].iloc[-1]),
            "high": round(hist['High'].max(), 2),
            "low": round(hist['Low'].min(), 2),
            "period": period,
            "company_name": info.get('longName', ticker),
            "sector": info.get('sector', 'N/A'),
            "market_cap": info.get('marketCap', 'N/A')
        }
    except Exception as e:
        return {"error": f"Error fetching data for {ticker}: {str(e)}"}


yahoo_finance_tool = adk.FunctionTool(
    function_declarations=[
        adk.FunctionDeclaration(
            name="get_stock_data",
            description="Fetch real-time stock market data from Yahoo Finance including price, volume, and company information",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"],
                        "description": "Time period for historical data",
                        "default": "1mo"
                    }
                },
                "required": ["ticker"]
            }
        )
    ]
)


# ============================================================================
# TOOL 2: CSV File Data Tool (Custom)
# ============================================================================
def read_csv_data(file_path: str, max_rows: int = 100) -> dict:
    """
    Read and analyze data from a CSV file.

    Args:
        file_path: Path to the CSV file
        max_rows: Maximum number of rows to return (default: 100)

    Returns:
        Dictionary containing CSV data, statistics, and column information
    """
    try:
        df = pd.read_csv(file_path)

        # Get basic statistics
        stats = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                stats[col] = {
                    "mean": round(df[col].mean(), 2) if not df[col].isna().all() else None,
                    "min": round(df[col].min(), 2) if not df[col].isna().all() else None,
                    "max": round(df[col].max(), 2) if not df[col].isna().all() else None
                }

        # Get sample data
        sample_data = df.head(max_rows).to_dict(orient='records')

        return {
            "file_path": file_path,
            "rows": len(df),
            "columns": list(df.columns),
            "column_count": len(df.columns),
            "statistics": stats,
            "sample_data": sample_data[:10],  # Return first 10 rows as sample
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    except Exception as e:
        return {"error": f"Error reading CSV file: {str(e)}"}


def query_csv_data(file_path: str, query: str) -> dict:
    """
    Query CSV data using pandas operations.

    Args:
        file_path: Path to the CSV file
        query: Query string (e.g., "Name == 'Aditya Birla SL Flexi Cap Fund'")

    Returns:
        Dictionary containing query results
    """
    try:
        df = pd.read_csv(file_path)
        result = df.query(query)

        return {
            "file_path": file_path,
            "query": query,
            "matches": len(result),
            "results": result.to_dict(orient='records')
        }
    except Exception as e:
        return {"error": f"Error querying CSV: {str(e)}"}


csv_tool = adk.FunctionTool(
    function_declarations=[
        adk.FunctionDeclaration(
            name="read_csv_data",
            description="Read and analyze data from a CSV file, providing statistics and sample data",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the CSV file"
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": "Maximum number of rows to analyze (default: 100)",
                        "default": 100
                    }
                },
                "required": ["file_path"]
            }
        ),
        adk.FunctionDeclaration(
            name="query_csv_data",
            description="Query CSV data using pandas query syntax (e.g., \"Name == 'Fund Name'\" or \"Returns > 10\")",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the CSV file"
                    },
                    "query": {
                        "type": "string",
                        "description": "Pandas query string to filter data"
                    }
                },
                "required": ["file_path", "query"]
            }
        )
    ]
)


# ============================================================================
# MAIN: Create ADK Agent with All 4 Tools
# ============================================================================
def create_adk_agent_with_tools():
    """
    Create an ADK agent with all 4 tools:
    1. Yahoo Finance (custom)
    2. Google Search (built-in)
    3. Code Execution (built-in)
    4. CSV Data (custom)
    """

    # Initialize the model
    model = adk.get_model(
        model_name="gemini-2.5-flash",
        api_key=GEMINI_API_KEY
    )

    # Create tools list combining custom and built-in tools
    tools = [
        yahoo_finance_tool,          # Custom Yahoo Finance tool
        csv_tool,                     # Custom CSV data tool
        adk.google_search(),          # Built-in Google Search tool
        adk.BuiltInCodeExecutor()     # Built-in Code Execution tool
    ]

    # Create the agent
    agent = adk.LlmAgent(
        model=model,
        tools=tools,
        name="MultiToolAgent",
        description="An agent with Yahoo Finance, Google Search, Code Execution, and CSV data tools"
    )

    return agent


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
async def run_example_queries():
    """Run example queries demonstrating all 4 tools"""

    print("=" * 80)
    print("ADK AGENT WITH 4 ESSENTIAL TOOLS")
    print("=" * 80)

    # Create the agent
    agent = create_adk_agent_with_tools()

    # Create a session
    session_service = adk.InMemorySessionService()
    session = session_service.create_session()

    # Create a runner
    runner = adk.Runner(
        agent=agent,
        session_service=session_service
    )

    # Example queries demonstrating each tool
    queries = [
        # Tool 1: Yahoo Finance
        "Get the current stock price and information for Apple (AAPL)",

        # Tool 2: CSV Data
        "Read and analyze the data from 'real_mutual_funds.csv' file",

        # Tool 3: Google Search
        "Search Google for 'best mutual funds 2024'",

        # Tool 4: Code Execution
        "Execute Python code to calculate the compound interest on $10000 at 7% for 5 years"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {i}: {query}")
        print(f"{'='*80}\n")

        # Run the query
        result = await runner.run(
            session_id=session.id,
            new_message=query
        )

        # Display the result
        print(f"Response: {result.content}\n")

    print("=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)


# ============================================================================
# MANUAL TOOL TESTING (Without Full Agent Setup)
# ============================================================================
def test_tools_manually():
    """Test each tool individually without requiring API keys"""

    print("\n" + "=" * 80)
    print("MANUAL TOOL TESTING (No API Required)")
    print("=" * 80)

    # Test 1: Yahoo Finance Tool
    print("\n1. YAHOO FINANCE TOOL")
    print("-" * 40)
    result = get_stock_data("AAPL", "1mo")
    print(f"Stock Data: {result}")

    # Test 2: CSV Tool
    print("\n2. CSV DATA TOOL")
    print("-" * 40)
    if os.path.exists('real_mutual_funds.csv'):
        result = read_csv_data('real_mutual_funds.csv', max_rows=5)
        print(f"CSV Analysis:")
        print(f"  - Rows: {result.get('rows')}")
        print(f"  - Columns: {result.get('column_count')}")
        print(f"  - Column Names: {result.get('columns')[:5]}...")  # First 5 columns
    else:
        print("  CSV file not found!")

    # Test 3 & 4: Google Search and Code Execution require API setup
    print("\n3. GOOGLE SEARCH TOOL (Built-in)")
    print("-" * 40)
    print("  Requires ADK agent setup with API key")

    print("\n4. CODE EXECUTION TOOL (Built-in)")
    print("-" * 40)
    print("  Requires ADK agent setup with API key")

    print("\n" + "=" * 80)


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    import sys

    print("\n" + "=" * 80)
    print("ADK TOOLS EXAMPLE - 4 Essential Tools")
    print("=" * 80)
    print("\nThis example demonstrates:")
    print("  1. Yahoo Finance Tool (custom)")
    print("  2. CSV Data Tool (custom)")
    print("  3. Google Search Tool (built-in)")
    print("  4. Code Execution Tool (built-in)")
    print("=" * 80)

    # Check if API key is available
    if GEMINI_API_KEY == "your-api-key-here":
        print("\n⚠️  No GEMINI_API_KEY found. Running manual tool tests only...")
        test_tools_manually()
    else:
        print("\n✅ API key found. Running full agent examples...")
        import asyncio
        asyncio.run(run_example_queries())

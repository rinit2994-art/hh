#!/usr/bin/env python3
"""
ADK Individual Tool Examples
=============================
Each tool demonstrated separately for easy learning
"""

import os
import pandas as pd
import yfinance as yf
from google.generativeai import genai_adk_dev as adk


# ============================================================================
# EXAMPLE 1: Yahoo Finance Tool
# ============================================================================
def example_1_yahoo_finance():
    """
    Example 1: Yahoo Finance Tool
    Fetch real-time stock market data
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: YAHOO FINANCE TOOL")
    print("="*80)

    # Define the function
    def get_stock_data(ticker: str, period: str = "1mo") -> dict:
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period=period)

            if hist.empty:
                return {"error": f"No data found for {ticker}"}

            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[0]
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100

            return {
                "ticker": ticker.upper(),
                "current_price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "company_name": info.get('longName', ticker),
                "sector": info.get('sector', 'N/A')
            }
        except Exception as e:
            return {"error": str(e)}

    # Create the ADK tool
    yahoo_finance_tool = adk.FunctionTool(
        function_declarations=[
            adk.FunctionDeclaration(
                name="get_stock_data",
                description="Fetch real-time stock data from Yahoo Finance",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "period": {
                            "type": "string",
                            "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
                            "description": "Time period",
                            "default": "1mo"
                        }
                    },
                    "required": ["ticker"]
                }
            )
        ]
    )

    # Test the function directly
    print("\nDirect function call:")
    result = get_stock_data("AAPL", "1mo")
    print(f"  Apple Stock: ${result.get('current_price')}")
    print(f"  Change: {result.get('change_percent')}%")
    print(f"  Sector: {result.get('sector')}")

    print("\n✅ Yahoo Finance Tool created successfully!")
    print(f"   Tool can be added to ADK agent with: tools=[yahoo_finance_tool]")

    return yahoo_finance_tool


# ============================================================================
# EXAMPLE 2: Google Search Tool (Built-in)
# ============================================================================
def example_2_google_search():
    """
    Example 2: Google Search Tool
    Built-in ADK tool for web searches
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: GOOGLE SEARCH TOOL (Built-in)")
    print("="*80)

    # Create the built-in Google Search tool
    google_search_tool = adk.google_search()

    print("\nGoogle Search Tool:")
    print("  - Built into ADK framework")
    print("  - No custom code needed")
    print("  - Performs Google searches automatically")

    print("\n✅ Google Search Tool ready!")
    print(f"   Tool can be added to ADK agent with: tools=[adk.google_search()]")

    return google_search_tool


# ============================================================================
# EXAMPLE 3: Code Execution Tool (Built-in)
# ============================================================================
def example_3_code_execution():
    """
    Example 3: Code Execution Tool
    Built-in ADK tool for running Python code
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: CODE EXECUTION TOOL (Built-in)")
    print("="*80)

    # Create the built-in Code Executor
    code_executor_tool = adk.BuiltInCodeExecutor()

    print("\nCode Execution Tool:")
    print("  - Built into ADK framework")
    print("  - Executes Python code safely")
    print("  - Returns execution results")

    print("\n✅ Code Execution Tool ready!")
    print(f"   Tool can be added to ADK agent with: tools=[adk.BuiltInCodeExecutor()]")

    return code_executor_tool


# ============================================================================
# EXAMPLE 4: CSV Data Tool
# ============================================================================
def example_4_csv_data():
    """
    Example 4: CSV Data Tool
    Read and analyze CSV files
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: CSV DATA TOOL")
    print("="*80)

    # Define the function
    def read_csv_data(file_path: str, max_rows: int = 100) -> dict:
        """Read and analyze CSV file"""
        try:
            df = pd.read_csv(file_path)

            # Get statistics for numeric columns
            stats = {}
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    stats[col] = {
                        "mean": round(df[col].mean(), 2),
                        "min": round(df[col].min(), 2),
                        "max": round(df[col].max(), 2)
                    }

            return {
                "file_path": file_path,
                "rows": len(df),
                "columns": list(df.columns),
                "statistics": stats,
                "sample_data": df.head(5).to_dict(orient='records')
            }
        except Exception as e:
            return {"error": str(e)}

    # Create the ADK tool
    csv_tool = adk.FunctionTool(
        function_declarations=[
            adk.FunctionDeclaration(
                name="read_csv_data",
                description="Read and analyze CSV file data",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to CSV file"
                        },
                        "max_rows": {
                            "type": "integer",
                            "description": "Max rows to analyze",
                            "default": 100
                        }
                    },
                    "required": ["file_path"]
                }
            )
        ]
    )

    # Test the function directly
    print("\nDirect function call:")
    if os.path.exists('real_mutual_funds.csv'):
        result = read_csv_data('real_mutual_funds.csv', 5)
        print(f"  File: {result.get('file_path')}")
        print(f"  Rows: {result.get('rows')}")
        print(f"  Columns: {result.get('columns', [])[:3]}... ({len(result.get('columns', []))} total)")
    else:
        print("  CSV file not found (will work when file exists)")

    print("\n✅ CSV Data Tool created successfully!")
    print(f"   Tool can be added to ADK agent with: tools=[csv_tool]")

    return csv_tool


# ============================================================================
# EXAMPLE 5: Combining All Tools in One Agent
# ============================================================================
def example_5_combined_agent():
    """
    Example 5: Create an agent with all 4 tools
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: COMBINED AGENT WITH ALL 4 TOOLS")
    print("="*80)

    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key or api_key == "your-api-key-here":
        print("\n⚠️  No GEMINI_API_KEY found.")
        print("   To run the full agent, set your API key:")
        print("   export GEMINI_API_KEY='your-key-here'")
        return None

    # Create all tools
    print("\nCreating tools...")

    # Custom tools
    yahoo_finance_tool = example_1_yahoo_finance()
    csv_tool = example_4_csv_data()

    # Built-in tools
    google_search_tool = adk.google_search()
    code_executor_tool = adk.BuiltInCodeExecutor()

    # Create model
    print("\nInitializing Gemini model...")
    model = adk.get_model(
        model_name="gemini-2.5-flash",
        api_key=api_key
    )

    # Create agent with all tools
    print("\nCreating agent with all 4 tools...")
    agent = adk.LlmAgent(
        model=model,
        tools=[
            yahoo_finance_tool,
            csv_tool,
            google_search_tool,
            code_executor_tool
        ],
        name="MultiToolAgent",
        description="Agent with Yahoo Finance, CSV, Google Search, and Code Execution"
    )

    print("\n✅ Agent created successfully with 4 tools!")
    print("\nExample usage:")
    print("""
    session_service = adk.InMemorySessionService()
    session = session_service.create_session()
    runner = adk.Runner(agent=agent, session_service=session_service)

    result = await runner.run(
        session_id=session.id,
        new_message="Get Apple stock price and search for recent news"
    )
    """)

    return agent


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Run all examples"""

    print("\n" + "="*80)
    print("ADK TOOLS - INDIVIDUAL EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates each tool individually:")
    print("  1. Yahoo Finance (Custom)")
    print("  2. Google Search (Built-in)")
    print("  3. Code Execution (Built-in)")
    print("  4. CSV Data (Custom)")
    print("  5. Combined Agent (All tools)")
    print("="*80)

    # Run each example
    example_1_yahoo_finance()
    example_2_google_search()
    example_3_code_execution()
    example_4_csv_data()
    example_5_combined_agent()

    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80)
    print("\nNext steps:")
    print("  1. Set GEMINI_API_KEY environment variable")
    print("  2. Run: python adk_tools_example.py")
    print("  3. Or use individual tools in your own code")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

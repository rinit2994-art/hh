# ADK Tools Example - 4 Essential Tools

This example demonstrates how to use the Agent Development Kit (ADK) with 4 essential tools:

## Tools Included

### 1. **Yahoo Finance Tool** (Custom)
- Fetches real-time stock market data
- Provides price, volume, company info, sector, market cap
- Supports multiple time periods (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y)

**Example Usage:**
```python
get_stock_data("AAPL", "1mo")  # Get Apple stock data for last month
```

### 2. **CSV Data Tool** (Custom)
- Reads and analyzes CSV files
- Provides statistics (mean, min, max) for numeric columns
- Supports querying with pandas syntax
- Returns sample data and column information

**Example Usage:**
```python
read_csv_data("real_mutual_funds.csv", max_rows=100)
query_csv_data("real_mutual_funds.csv", "Returns > 10")
```

### 3. **Google Search Tool** (Built-in ADK)
- Performs Google searches
- Returns relevant search results
- Built into ADK framework

**Example Usage:**
```python
adk.google_search()  # Built-in tool
```

### 4. **Code Execution Tool** (Built-in ADK)
- Executes Python code safely
- Returns execution results
- Built into ADK framework

**Example Usage:**
```python
adk.BuiltInCodeExecutor()  # Built-in tool
```

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements_adk.txt
   ```

2. **Set up API key:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

3. **Run the example:**
   ```bash
   python adk_tools_example.py
   ```

## Usage Modes

### Full Agent Mode (Requires API Key)
When `GEMINI_API_KEY` is set, the script runs a complete ADK agent with all 4 tools, demonstrating:
- Stock data retrieval
- CSV data analysis
- Google searches
- Code execution

### Manual Testing Mode (No API Key Required)
Without an API key, the script tests custom tools directly:
- Yahoo Finance tool
- CSV data tool

## Example Queries

The script includes example queries for each tool:

1. **Yahoo Finance:** "Get the current stock price and information for Apple (AAPL)"
2. **CSV Data:** "Read and analyze the data from 'real_mutual_funds.csv' file"
3. **Google Search:** "Search Google for 'best mutual funds 2024'"
4. **Code Execution:** "Execute Python code to calculate compound interest"

## Code Structure

```
adk_tools_example.py
├── Tool 1: Yahoo Finance (Custom)
│   ├── get_stock_data() function
│   └── yahoo_finance_tool FunctionTool
├── Tool 2: CSV Data (Custom)
│   ├── read_csv_data() function
│   ├── query_csv_data() function
│   └── csv_tool FunctionTool
├── Tool 3 & 4: Built-in Tools
│   ├── adk.google_search()
│   └── adk.BuiltInCodeExecutor()
└── Agent Setup
    ├── create_adk_agent_with_tools()
    ├── run_example_queries()
    └── test_tools_manually()
```

## Key Features

- **Custom Tool Creation:** Shows how to create custom tools using `FunctionTool`
- **Built-in Tools:** Demonstrates using ADK's built-in tools
- **Combined Agent:** Shows how to combine multiple tools in one agent
- **Error Handling:** Includes proper error handling for all tools
- **Flexible Testing:** Works with or without API keys

## Integration with Your Project

This example can be integrated with your existing mutual funds project:

```python
# Use CSV tool with your mutual fund data
csv_result = read_csv_data('real_mutual_funds.csv')

# Use Yahoo Finance to get real-time market data
stock_data = get_stock_data('SPY', '1mo')  # S&P 500 ETF

# Combine with agent for intelligent analysis
agent = create_adk_agent_with_tools()
result = await runner.run(
    session_id=session.id,
    new_message="Analyze the top performing mutual funds from the CSV and compare with current market trends"
)
```

## API Key Setup

To use Google's Gemini API:

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Set the environment variable:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```

## Notes

- Yahoo Finance data is free and doesn't require API keys
- Google Search and Code Execution require Gemini API access
- CSV tool works with any pandas-compatible CSV file
- All tools include comprehensive error handling

## Example Output

```
QUERY 1: Get the current stock price and information for Apple (AAPL)
Response: Apple (AAPL) is currently trading at $175.23, up $2.15 (+1.24%)
over the last month. Market cap: $2.73T, Sector: Technology

QUERY 2: Read and analyze the data from 'real_mutual_funds.csv' file
Response: Analyzed 18 mutual funds with 52 columns. Top performers include...

QUERY 3: Search Google for 'best mutual funds 2024'
Response: Found several resources discussing top mutual funds for 2024...

QUERY 4: Execute Python code to calculate compound interest
Response: The compound interest on $10,000 at 7% for 5 years is $4,025.52
```

## License

This is example code for demonstration purposes.

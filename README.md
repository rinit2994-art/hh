# Mutual Fund Analysis Multi-Agent System

A sophisticated multi-agent system built with Google's Agent Development Kit (ADK) for analyzing mutual funds, performing financial research, and providing data-driven investment insights.

## Overview

This system coordinates four specialized AI agents that work together to analyze mutual funds, fetch real-time financial data, process CSV files, search for market information, and perform complex calculations.

## Architecture

### Agent Hierarchy

```
Coordinator Agent (Orchestrator)
├── Yahoo Finance Agent (Financial Data)
├── CSV Data Agent (File Operations)
├── Google Search Agent (Web Search)
└── Code Execution Agent (Calculations)
```

### Specialized Agents

#### 1. Yahoo Finance Agent
- **Purpose**: Fetch real-time and historical financial data
- **Capabilities**:
  - Get current stock quotes and mutual fund NAV
  - Retrieve historical price data
  - Search for ticker symbols by company name
  - Fetch mutual fund information and performance

#### 2. CSV Data Agent
- **Purpose**: Handle CSV file operations and data analysis
- **Capabilities**:
  - Read and summarize CSV files
  - Filter and query data
  - Aggregate data with grouping operations
  - Write data to CSV files
  - List available CSV files

#### 3. Google Search Agent
- **Purpose**: Search the web for information and research
- **Capabilities**:
  - Find news and current events
  - Research companies and market trends
  - Discover investment insights
  - Validate information from multiple sources

#### 4. Code Execution Agent
- **Purpose**: Execute Python code for data analysis
- **Capabilities**:
  - Execute Python code with pandas and numpy
  - Analyze DataFrames with statistical operations
  - Calculate statistics and performance metrics
  - Perform mathematical calculations
  - Transform data (normalize, standardize, log transform)

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Install Dependencies

```bash
pip install google-adk pandas numpy requests
```

## Usage

### Interactive Mode

Run the system in interactive mode to ask questions:

```bash
python main.py
```

Then enter your queries:
```
You: What are the top mutual funds in sample_mutual_funds.csv?
You: Get the current price of VTSAX
You: Search for recent mutual fund investment strategies
You: Calculate the average return of all funds in the CSV
```

### Example Queries Mode

Run pre-configured example queries:

```bash
python main.py --examples
```

## Example Use Cases

### 1. Analyze Mutual Fund Data from CSV

```
Query: "Read sample_mutual_funds.csv and show me the top 5 funds by 1 Year Return"
```

The system will:
1. CSV Agent reads the file
2. Code Execution Agent sorts and filters the data
3. Coordinator presents the top performers

### 2. Research a Specific Fund

```
Query: "Analyze the VTSAX mutual fund"
```

The system will:
1. Yahoo Finance Agent fetches current NAV and performance
2. Google Search Agent finds recent news and analysis
3. Code Execution Agent calculates performance metrics
4. Coordinator provides comprehensive analysis

### 3. Compare Fund Performance

```
Query: "Compare the returns of all funds in real_mutual_funds.csv and tell me which ones outperformed the market"
```

The system will:
1. CSV Agent loads the data
2. Code Execution Agent calculates comparative metrics
3. Yahoo Finance Agent gets current market benchmarks
4. Coordinator provides ranking and recommendations

### 4. Market Research

```
Query: "What are the current trends in mutual fund investments?"
```

The system will:
1. Google Search Agent finds recent articles and trends
2. Yahoo Finance Agent gets market data
3. Coordinator synthesizes insights

## Available Tools

### Yahoo Finance Agent Tools
- `fetch_stock_quote(symbol)` - Get current price
- `fetch_stock_history(symbol, period)` - Get historical data
- `search_ticker_symbol(company_name)` - Find ticker symbols
- `get_mutual_fund_info(symbol)` - Get mutual fund details

### CSV Data Agent Tools
- `read_csv_file(file_path, rows)` - Read CSV data
- `get_csv_summary(file_path)` - Get statistics
- `filter_csv_data(file_path, column, value, operator)` - Filter data
- `aggregate_csv_data(file_path, group_by, agg_column, operation)` - Aggregate
- `write_csv_file(file_path, data)` - Write CSV
- `list_csv_files(directory)` - List CSV files

### Code Execution Agent Tools
- `execute_python_code(code)` - Execute Python code
- `analyze_dataframe(data, operations)` - Analyze data
- `calculate_statistics(numbers)` - Calculate stats
- `perform_calculation(expression)` - Math calculations
- `transform_data(data, transformation)` - Data transformations

### Google Search Agent Tools
- `google_search` - Search the web (built-in ADK tool)

## Project Structure

```
hh/
├── agents/
│   ├── __init__.py
│   ├── yahoo_finance_agent.py    # Financial data agent
│   ├── csv_agent.py               # CSV operations agent
│   ├── google_search_agent.py     # Web search agent
│   ├── code_execution_agent.py    # Code execution agent
│   └── coordinator.py             # Coordinator agent
├── main.py                        # Main application
├── sample_mutual_funds.csv        # Sample data
├── real_mutual_funds.csv          # Real fund data
└── README.md                      # This file
```

## Data Files

The repository includes sample mutual fund data:
- `sample_mutual_funds.csv` - Sample mutual fund data for testing
- `real_mutual_funds.csv` - Real mutual fund data

## Features

✅ **Multi-Agent Coordination**: Intelligent orchestration of specialized agents
✅ **Real-Time Financial Data**: Live quotes and mutual fund NAV from Yahoo Finance
✅ **CSV Data Processing**: Advanced file operations and analysis
✅ **Web Search Integration**: Google Search for research and news
✅ **Code Execution**: Python-based calculations and data transformations
✅ **Natural Language Interface**: Ask questions in plain English
✅ **Comprehensive Analysis**: Combines multiple data sources for insights

## Technical Details

- **Framework**: Google Agent Development Kit (ADK)
- **Model**: Gemini 2.0 Flash Exp
- **Language**: Python 3.8+
- **Key Libraries**: pandas, numpy, requests
- **Architecture**: Hierarchical multi-agent system

## Configuration

### Environment Variables

You may need to set the following environment variables:

```bash
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_PROJECT_ID="your-project-id"
```

### Model Configuration

Each agent uses `gemini-2.0-flash-exp` by default. You can modify the model in each agent file if needed.

## Development

### Adding New Agents

1. Create a new agent file in `agents/` directory
2. Define tools as Python functions
3. Create an `LlmAgent` instance with tools
4. Add the agent to `coordinator.py` as a sub-agent
5. Update `agents/__init__.py`

### Adding New Tools

1. Define a Python function with type hints
2. Add docstring describing the function
3. Add the function to the agent's `tools` list

## Limitations

- Yahoo Finance data depends on public APIs (rate limits may apply)
- Google Search requires appropriate API access
- Code execution is sandboxed for safety
- Large CSV files may take time to process

## Future Enhancements

- [ ] Add visualization capabilities
- [ ] Implement portfolio optimization
- [ ] Add more financial data sources
- [ ] Create web UI interface
- [ ] Add deployment to Cloud Run/Vertex AI
- [ ] Implement caching for repeated queries
- [ ] Add support for Excel files
- [ ] Include backtesting capabilities

## License

This project uses Google's ADK which is licensed under Apache 2.0.

## Support

For issues related to:
- **ADK**: Visit [adk-python repository](https://github.com/google/adk-python)
- **This project**: Create an issue in the repository

## Acknowledgments

Built with Google's Agent Development Kit (ADK) - an open-source framework for building AI agents.

---

**Happy Investing! 📈**

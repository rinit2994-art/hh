#!/usr/bin/env python3
"""
Demo script for the Mutual Fund Analysis Multi-Agent System.

This script demonstrates the capabilities of each agent without requiring
an API key for the runtime.
"""

import os
import sys


def demo_csv_agent():
    """Demonstrate CSV agent capabilities."""
    print("\n" + "=" * 70)
    print("DEMO: CSV Data Agent")
    print("=" * 70)

    from agents.csv_agent import (
        list_csv_files,
        get_csv_summary,
        read_csv_file,
        filter_csv_data
    )

    # List CSV files
    print("\n1. Listing CSV files in current directory:")
    result = list_csv_files(".")
    for file_info in result.get('csv_files', []):
        print(f"   - {file_info['name']} ({file_info['size_kb']} KB)")

    # Get CSV summary
    if result.get('csv_files'):
        csv_file = result['csv_files'][0]['path']
        print(f"\n2. Summary of {csv_file}:")
        summary = get_csv_summary(csv_file)
        print(f"   - Total rows: {summary.get('total_rows')}")
        print(f"   - Total columns: {summary.get('total_columns')}")
        print(f"   - Columns: {', '.join(summary.get('columns', [])[:5])}...")

        # Read first 5 rows
        print(f"\n3. First 5 rows of data:")
        data = read_csv_file(csv_file, rows=5)
        if data.get('preview'):
            for i, row in enumerate(data['preview'][:3], 1):
                fund_name = row.get('Scheme Name', row.get('name', 'N/A'))
                print(f"   {i}. {fund_name}")


def demo_code_execution_agent():
    """Demonstrate code execution agent capabilities."""
    print("\n" + "=" * 70)
    print("DEMO: Code Execution Agent")
    print("=" * 70)

    from agents.code_execution_agent import (
        calculate_statistics,
        perform_calculation,
        analyze_dataframe
    )

    # Calculate statistics
    print("\n1. Calculating statistics for sample data:")
    numbers = [10.5, 12.3, 8.9, 15.2, 11.7, 9.8, 14.1, 10.2]
    result = calculate_statistics(numbers)
    print(f"   - Mean: {result.get('mean'):.2f}")
    print(f"   - Median: {result.get('median'):.2f}")
    print(f"   - Std Dev: {result.get('std'):.2f}")
    print(f"   - Min/Max: {result.get('min'):.2f} / {result.get('max'):.2f}")

    # Perform calculation
    print("\n2. Performing calculations:")
    calculations = [
        ("sqrt(144)", "Square root of 144"),
        ("10 * 1.08 ** 5", "Compound interest: $10 at 8% for 5 years"),
        ("(100 - 85) / 85 * 100", "Percentage return: from 85 to 100")
    ]

    for expr, desc in calculations:
        result = perform_calculation(expr)
        if result.get('status') == 'success':
            print(f"   - {desc}: {result.get('result'):.2f}")

    # Analyze dataframe
    print("\n3. Analyzing mutual fund data:")
    sample_data = [
        {'fund': 'Fund A', 'return_1yr': 12.5, 'return_3yr': 15.2, 'expense_ratio': 0.5},
        {'fund': 'Fund B', 'return_1yr': 10.3, 'return_3yr': 12.8, 'expense_ratio': 0.75},
        {'fund': 'Fund C', 'return_1yr': 14.7, 'return_3yr': 18.1, 'expense_ratio': 0.45},
    ]

    result = analyze_dataframe(sample_data, ['mean', 'describe'])
    if result.get('status') == 'success':
        means = result['results']['operations']['mean']
        print(f"   - Average 1-year return: {means.get('return_1yr', 0):.2f}%")
        print(f"   - Average 3-year return: {means.get('return_3yr', 0):.2f}%")
        print(f"   - Average expense ratio: {means.get('expense_ratio', 0):.2f}%")


def demo_yahoo_finance_agent():
    """Demonstrate Yahoo Finance agent capabilities."""
    print("\n" + "=" * 70)
    print("DEMO: Yahoo Finance Agent")
    print("=" * 70)

    from agents.yahoo_finance_agent import (
        fetch_stock_quote,
        search_ticker_symbol
    )

    print("\n1. Searching for ticker symbols:")
    companies = ["Vanguard", "Fidelity"]

    for company in companies:
        result = search_ticker_symbol(company)
        if 'error' not in result and result.get('results'):
            print(f"   - {company}:")
            for ticker in result['results'][:2]:
                print(f"     • {ticker.get('symbol')}: {ticker.get('name')}")
        else:
            print(f"   - {company}: Note - Yahoo Finance may have rate limits")

    print("\n2. Note: Live price fetching may require proper headers/API access")
    print("   The system is configured but may hit rate limits in demo mode")


def demo_coordinator():
    """Demonstrate the coordinator's capabilities."""
    print("\n" + "=" * 70)
    print("DEMO: Coordinator Agent")
    print("=" * 70)

    from agents.coordinator import coordinator_agent

    print(f"\nCoordinator: {coordinator_agent.name}")
    print(f"Model: {coordinator_agent.model}")
    print(f"\nOrchestrates {len(coordinator_agent.sub_agents)} specialized agents:")

    for i, agent in enumerate(coordinator_agent.sub_agents, 1):
        print(f"\n{i}. {agent.name}")
        print(f"   - Tools: {len(agent.tools)}")
        print(f"   - Description: {agent.description[:80]}...")

    print("\n" + "=" * 70)
    print("Typical Workflow:")
    print("=" * 70)
    print("""
    1. User Query: "Analyze the best performing mutual funds in my CSV"

    2. Coordinator routes to:
       → CSV Agent: Read and analyze the CSV file
       → Code Execution Agent: Calculate performance metrics
       → Yahoo Finance Agent: Get current NAV for top funds
       → Google Search Agent: Find recent news about top performers

    3. Coordinator synthesizes results and provides recommendations
    """)


def demo_example_use_cases():
    """Show example use cases."""
    print("\n" + "=" * 70)
    print("EXAMPLE USE CASES")
    print("=" * 70)

    use_cases = [
        {
            "title": "Find Top Performers",
            "query": "What are the top 5 mutual funds by 1-year return in sample_mutual_funds.csv?",
            "agents": ["CSV Agent", "Code Execution Agent"]
        },
        {
            "title": "Compare Funds",
            "query": "Compare expense ratios across different fund categories",
            "agents": ["CSV Agent", "Code Execution Agent"]
        },
        {
            "title": "Research Fund",
            "query": "Get detailed information about VTSAX including current price and news",
            "agents": ["Yahoo Finance Agent", "Google Search Agent"]
        },
        {
            "title": "Portfolio Analysis",
            "query": "Calculate the risk and return profile of my portfolio in the CSV",
            "agents": ["CSV Agent", "Code Execution Agent", "Yahoo Finance Agent"]
        },
        {
            "title": "Market Trends",
            "query": "What are the current trends in mutual fund investing?",
            "agents": ["Google Search Agent", "Yahoo Finance Agent"]
        }
    ]

    for i, use_case in enumerate(use_cases, 1):
        print(f"\n{i}. {use_case['title']}")
        print(f"   Query: \"{use_case['query']}\"")
        print(f"   Agents Used: {', '.join(use_case['agents'])}")


def main():
    """Run all demos."""
    print("=" * 70)
    print("MUTUAL FUND ANALYSIS MULTI-AGENT SYSTEM - DEMO")
    print("=" * 70)
    print("\nThis demo showcases the capabilities of the 4 specialized agents")
    print("without requiring a full runtime environment.\n")

    demos = [
        ("CSV Data Agent", demo_csv_agent),
        ("Code Execution Agent", demo_code_execution_agent),
        ("Yahoo Finance Agent", demo_yahoo_finance_agent),
        ("Coordinator Agent", demo_coordinator),
        ("Example Use Cases", demo_example_use_cases)
    ]

    for title, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ Error in {title} demo: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nTo run the full interactive system, use: python main.py")
    print("To run example queries, use: python main.py --examples")
    print("\nNote: Full functionality requires proper Google Cloud credentials")
    print("=" * 70)


if __name__ == "__main__":
    main()

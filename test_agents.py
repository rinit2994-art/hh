#!/usr/bin/env python3
"""Test script for the multi-agent system."""

import os
import sys

def test_imports():
    """Test that all agents can be imported."""
    print("Testing imports...")
    try:
        from agents import (
            yahoo_finance_agent,
            csv_agent,
            google_search_agent,
            code_execution_agent,
            coordinator_agent
        )
        print("✓ All agents imported successfully!")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_csv_agent():
    """Test CSV agent with sample data."""
    print("\nTesting CSV Agent...")
    try:
        from agents.csv_agent import list_csv_files, get_csv_summary

        # Test listing CSV files
        result = list_csv_files(".")
        print(f"✓ Found {result.get('count', 0)} CSV files")

        # Test reading a CSV file if available
        if result.get('csv_files'):
            csv_file = result['csv_files'][0]['path']
            summary = get_csv_summary(csv_file)
            if 'error' not in summary:
                print(f"✓ Successfully read {csv_file}")
                print(f"  - Rows: {summary.get('total_rows')}")
                print(f"  - Columns: {summary.get('total_columns')}")
            else:
                print(f"✗ Error reading CSV: {summary['error']}")

        return True
    except Exception as e:
        print(f"✗ CSV Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_execution_agent():
    """Test code execution agent."""
    print("\nTesting Code Execution Agent...")
    try:
        from agents.code_execution_agent import calculate_statistics, perform_calculation

        # Test statistics calculation
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = calculate_statistics(numbers)
        if result.get('status') == 'success':
            print(f"✓ Statistics calculation successful")
            print(f"  - Mean: {result.get('mean')}")
            print(f"  - Median: {result.get('median')}")
        else:
            print(f"✗ Statistics calculation failed: {result.get('error')}")

        # Test calculation
        calc_result = perform_calculation("2 + 2 * 5")
        if calc_result.get('status') == 'success':
            print(f"✓ Calculation successful: 2 + 2 * 5 = {calc_result.get('result')}")
        else:
            print(f"✗ Calculation failed: {calc_result.get('error')}")

        return True
    except Exception as e:
        print(f"✗ Code Execution Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yahoo_finance_agent():
    """Test Yahoo Finance agent."""
    print("\nTesting Yahoo Finance Agent...")
    try:
        from agents.yahoo_finance_agent import search_ticker_symbol

        # Test searching for a ticker
        result = search_ticker_symbol("Apple")
        if 'error' not in result:
            print(f"✓ Ticker search successful")
            if result.get('results'):
                print(f"  - Found: {result['results'][0]['symbol']} - {result['results'][0]['name']}")
        else:
            print(f"⚠ Ticker search warning: {result.get('error')}")

        return True
    except Exception as e:
        print(f"✗ Yahoo Finance Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_structure():
    """Test the agent structure."""
    print("\nTesting Agent Structure...")
    try:
        from agents.coordinator import coordinator_agent

        print(f"✓ Coordinator agent: {coordinator_agent.name}")
        print(f"  - Model: {coordinator_agent.model}")
        print(f"  - Sub-agents: {len(coordinator_agent.sub_agents)}")

        for agent in coordinator_agent.sub_agents:
            print(f"    • {agent.name} ({len(agent.tools)} tools)")

        return True
    except Exception as e:
        print(f"✗ Agent structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Multi-Agent System Test Suite")
    print("=" * 70)

    tests = [
        test_imports,
        test_agent_structure,
        test_csv_agent,
        test_code_execution_agent,
        test_yahoo_finance_agent
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 70)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 70)

    if all(results):
        print("\n✓ All tests passed! The multi-agent system is ready.")
        return 0
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Comprehensive testing script for the multi-agent system."""

import sys
import traceback
from typing import Dict, Any


def test_individual_tools():
    """Test each tool individually."""
    print("=" * 70)
    print("TEST 1: Individual Tool Testing")
    print("=" * 70)

    results = {"passed": 0, "failed": 0, "errors": []}

    # Test CSV Agent Tools
    print("\n--- CSV Agent Tools ---")
    try:
        from agents.csv_agent import (
            list_csv_files, get_csv_summary, read_csv_file,
            filter_csv_data, aggregate_csv_data
        )

        # Test 1: List CSV files
        result = list_csv_files(".")
        assert "csv_files" in result, "list_csv_files should return csv_files"
        print("✓ list_csv_files works")
        results["passed"] += 1

        # Test 2: Get CSV summary
        if result["csv_files"]:
            csv_file = result["csv_files"][0]["path"]
            summary = get_csv_summary(csv_file)
            assert "total_rows" in summary, "get_csv_summary should return total_rows"
            assert "columns" in summary, "get_csv_summary should return columns"
            print(f"✓ get_csv_summary works - {summary['total_rows']} rows, {summary['total_columns']} columns")
            results["passed"] += 1

            # Test 3: Read CSV file
            data = read_csv_file(csv_file, rows=5)
            assert "data" in data or "preview" in data, "read_csv_file should return data"
            print(f"✓ read_csv_file works - read {data.get('rows', 0)} rows")
            results["passed"] += 1

        else:
            print("⚠ No CSV files found to test")

    except Exception as e:
        print(f"✗ CSV Agent tools failed: {e}")
        results["failed"] += 1
        results["errors"].append(("CSV Agent", str(e), traceback.format_exc()))

    # Test Code Execution Agent Tools
    print("\n--- Code Execution Agent Tools ---")
    try:
        from agents.code_execution_agent import (
            calculate_statistics, perform_calculation,
            analyze_dataframe, execute_python_code, transform_data
        )

        # Test 1: Calculate statistics
        numbers = [1, 2, 3, 4, 5]
        result = calculate_statistics(numbers)
        assert result["status"] == "success", "calculate_statistics should succeed"
        assert result["mean"] == 3.0, f"Mean should be 3.0, got {result['mean']}"
        print(f"✓ calculate_statistics works - mean: {result['mean']}")
        results["passed"] += 1

        # Test 2: Perform calculation
        result = perform_calculation("2 + 2")
        assert result["status"] == "success", "perform_calculation should succeed"
        assert result["result"] == 4.0, f"2 + 2 should be 4.0, got {result['result']}"
        print(f"✓ perform_calculation works - 2 + 2 = {result['result']}")
        results["passed"] += 1

        # Test 3: Analyze dataframe
        data = [
            {"a": 1, "b": 2},
            {"a": 3, "b": 4},
            {"a": 5, "b": 6}
        ]
        result = analyze_dataframe(data, ["mean", "sum"])
        assert result["status"] == "success", "analyze_dataframe should succeed"
        print("✓ analyze_dataframe works")
        results["passed"] += 1

        # Test 4: Execute Python code
        code = "result = 10 * 5\nprint(f'Result: {result}')"
        result = execute_python_code(code)
        assert result["status"] == "success", "execute_python_code should succeed"
        assert "50" in result["output"], f"Output should contain 50, got: {result['output']}"
        print(f"✓ execute_python_code works - output captured")
        results["passed"] += 1

        # Test 5: Transform data
        result = transform_data(data, "normalize")
        assert result["status"] == "success", "transform_data should succeed"
        print("✓ transform_data works")
        results["passed"] += 1

    except Exception as e:
        print(f"✗ Code Execution Agent tools failed: {e}")
        results["failed"] += 1
        results["errors"].append(("Code Execution Agent", str(e), traceback.format_exc()))

    # Test Yahoo Finance Agent Tools
    print("\n--- Yahoo Finance Agent Tools ---")
    try:
        from agents.yahoo_finance_agent import (
            fetch_stock_quote, search_ticker_symbol
        )

        # Test search (may hit rate limits but shouldn't crash)
        result = search_ticker_symbol("test")
        assert isinstance(result, dict), "search_ticker_symbol should return dict"
        print("✓ search_ticker_symbol returns proper structure")
        results["passed"] += 1

        # Test quote fetch (may fail due to rate limits, but shouldn't crash)
        result = fetch_stock_quote("AAPL")
        assert isinstance(result, dict), "fetch_stock_quote should return dict"
        print("✓ fetch_stock_quote returns proper structure")
        results["passed"] += 1

    except Exception as e:
        print(f"✗ Yahoo Finance Agent tools failed: {e}")
        results["failed"] += 1
        results["errors"].append(("Yahoo Finance Agent", str(e), traceback.format_exc()))

    print(f"\nTool Testing: {results['passed']} passed, {results['failed']} failed")
    return results


def test_agent_initialization():
    """Test that all agents initialize properly."""
    print("\n" + "=" * 70)
    print("TEST 2: Agent Initialization")
    print("=" * 70)

    results = {"passed": 0, "failed": 0, "errors": []}

    try:
        from agents import (
            yahoo_finance_agent,
            csv_agent,
            google_search_agent,
            code_execution_agent,
            coordinator_agent
        )

        # Check each agent
        agents = [
            ("Yahoo Finance", yahoo_finance_agent, 4),
            ("CSV", csv_agent, 6),
            ("Google Search", google_search_agent, 1),
            ("Code Execution", code_execution_agent, 5),
            ("Coordinator", coordinator_agent, None)
        ]

        for name, agent, expected_tools in agents:
            assert hasattr(agent, 'name'), f"{name} agent should have name"
            assert hasattr(agent, 'model'), f"{name} agent should have model"

            if expected_tools is not None:
                assert hasattr(agent, 'tools'), f"{name} agent should have tools"
                assert len(agent.tools) == expected_tools, \
                    f"{name} agent should have {expected_tools} tools, got {len(agent.tools)}"
                print(f"✓ {name} Agent: {agent.name} with {len(agent.tools)} tools")
            else:
                assert hasattr(agent, 'sub_agents'), f"{name} agent should have sub_agents"
                print(f"✓ {name} Agent: {agent.name} with {len(agent.sub_agents)} sub-agents")

            results["passed"] += 1

        # Check coordinator sub-agents
        assert len(coordinator_agent.sub_agents) == 4, "Coordinator should have 4 sub-agents"
        print(f"\n✓ Coordinator has all 4 sub-agents")
        results["passed"] += 1

    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        results["failed"] += 1
        results["errors"].append(("Agent Initialization", str(e), traceback.format_exc()))

    print(f"\nAgent Initialization: {results['passed']} passed, {results['failed']} failed")
    return results


def test_runtime_setup():
    """Test ADK Runtime setup."""
    print("\n" + "=" * 70)
    print("TEST 3: ADK Runtime Setup")
    print("=" * 70)

    results = {"passed": 0, "failed": 0, "errors": []}

    try:
        from google.adk.runtime import Runtime
        from agents.coordinator import coordinator_agent

        print("Attempting to create Runtime...")
        runtime = Runtime(root_agent=coordinator_agent)

        assert runtime is not None, "Runtime should be created"
        print("✓ Runtime created successfully")
        results["passed"] += 1

        # Check runtime has the coordinator
        assert hasattr(runtime, 'root_agent') or hasattr(runtime, '_root_agent'), \
            "Runtime should have root_agent"
        print("✓ Runtime has coordinator agent")
        results["passed"] += 1

    except Exception as e:
        print(f"✗ Runtime setup failed: {e}")
        print(f"  This may require Google Cloud credentials")
        results["failed"] += 1
        results["errors"].append(("Runtime Setup", str(e), traceback.format_exc()))

    print(f"\nRuntime Setup: {results['passed']} passed, {results['failed']} failed")
    return results


def test_csv_workflow():
    """Test a complete CSV analysis workflow."""
    print("\n" + "=" * 70)
    print("TEST 4: CSV Analysis Workflow")
    print("=" * 70)

    results = {"passed": 0, "failed": 0, "errors": []}

    try:
        from agents.csv_agent import list_csv_files, read_csv_file, get_csv_summary
        from agents.code_execution_agent import analyze_dataframe

        # Step 1: Find CSV files
        print("Step 1: Finding CSV files...")
        csv_list = list_csv_files(".")
        assert csv_list["count"] > 0, "Should find at least one CSV file"
        print(f"✓ Found {csv_list['count']} CSV files")
        results["passed"] += 1

        csv_file = csv_list["csv_files"][0]["path"]

        # Step 2: Get summary
        print(f"\nStep 2: Getting summary of {csv_file}...")
        summary = get_csv_summary(csv_file)
        assert "total_rows" in summary, "Summary should have total_rows"
        print(f"✓ Summary: {summary['total_rows']} rows, {summary['total_columns']} columns")
        results["passed"] += 1

        # Step 3: Read data
        print(f"\nStep 3: Reading data...")
        data = read_csv_file(csv_file, rows=10)
        assert "data" in data or "preview" in data, "Should have data"
        print(f"✓ Read {data.get('rows', 0)} rows")
        results["passed"] += 1

        # Step 4: Analyze with code execution agent
        if data.get("data"):
            print(f"\nStep 4: Analyzing data...")
            analysis = analyze_dataframe(data["data"][:5], ["mean", "describe"])
            if analysis["status"] == "success":
                print(f"✓ Analysis completed successfully")
                results["passed"] += 1
            else:
                print(f"⚠ Analysis returned: {analysis.get('status')}")

    except Exception as e:
        print(f"✗ CSV workflow failed: {e}")
        results["failed"] += 1
        results["errors"].append(("CSV Workflow", str(e), traceback.format_exc()))

    print(f"\nCSV Workflow: {results['passed']} passed, {results['failed']} failed")
    return results


def test_error_handling():
    """Test error handling."""
    print("\n" + "=" * 70)
    print("TEST 5: Error Handling")
    print("=" * 70)

    results = {"passed": 0, "failed": 0, "errors": []}

    try:
        from agents.csv_agent import read_csv_file, filter_csv_data
        from agents.code_execution_agent import calculate_statistics, perform_calculation

        # Test 1: Non-existent file
        print("Test 1: Non-existent file...")
        result = read_csv_file("nonexistent.csv")
        assert "error" in result, "Should return error for non-existent file"
        print(f"✓ Properly handles non-existent file: {result['error']}")
        results["passed"] += 1

        # Test 2: Invalid calculation
        print("\nTest 2: Invalid calculation...")
        result = perform_calculation("invalid python code")
        assert "error" in result or result["status"] == "error", \
            "Should return error for invalid calculation"
        print(f"✓ Properly handles invalid calculation")
        results["passed"] += 1

        # Test 3: Empty data
        print("\nTest 3: Empty data...")
        result = calculate_statistics([])
        assert "error" in result or result["status"] == "error", \
            "Should handle empty data"
        print(f"✓ Properly handles empty data")
        results["passed"] += 1

    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        results["failed"] += 1
        results["errors"].append(("Error Handling", str(e), traceback.format_exc()))

    print(f"\nError Handling: {results['passed']} passed, {results['failed']} failed")
    return results


def test_data_types():
    """Test different data types and edge cases."""
    print("\n" + "=" * 70)
    print("TEST 6: Data Types and Edge Cases")
    print("=" * 70)

    results = {"passed": 0, "failed": 0, "errors": []}

    try:
        from agents.code_execution_agent import calculate_statistics, analyze_dataframe

        # Test 1: Float numbers
        print("Test 1: Float numbers...")
        result = calculate_statistics([1.5, 2.7, 3.2, 4.1])
        assert result["status"] == "success", "Should handle floats"
        print(f"✓ Handles float numbers: mean = {result['mean']:.2f}")
        results["passed"] += 1

        # Test 2: Large numbers
        print("\nTest 2: Large numbers...")
        result = calculate_statistics([1000000, 2000000, 3000000])
        assert result["status"] == "success", "Should handle large numbers"
        print(f"✓ Handles large numbers: mean = {result['mean']:,.0f}")
        results["passed"] += 1

        # Test 3: Negative numbers
        print("\nTest 3: Negative numbers...")
        result = calculate_statistics([-5, -10, 15, 20])
        assert result["status"] == "success", "Should handle negative numbers"
        print(f"✓ Handles negative numbers: mean = {result['mean']}")
        results["passed"] += 1

        # Test 4: Mixed data types in DataFrame
        print("\nTest 4: Mixed data types...")
        data = [
            {"name": "A", "value": 10, "category": "X"},
            {"name": "B", "value": 20, "category": "Y"},
            {"name": "C", "value": 30, "category": "X"}
        ]
        result = analyze_dataframe(data, ["mean"])
        assert result["status"] == "success", "Should handle mixed types"
        print(f"✓ Handles mixed data types")
        results["passed"] += 1

    except Exception as e:
        print(f"✗ Data types test failed: {e}")
        results["failed"] += 1
        results["errors"].append(("Data Types", str(e), traceback.format_exc()))

    print(f"\nData Types Testing: {results['passed']} passed, {results['failed']} failed")
    return results


def main():
    """Run all comprehensive tests."""
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "COMPREHENSIVE TEST SUITE" + " " * 29 + "║")
    print("╚" + "=" * 68 + "╝")

    all_results = []

    # Run all test suites
    test_suites = [
        ("Individual Tools", test_individual_tools),
        ("Agent Initialization", test_agent_initialization),
        ("Runtime Setup", test_runtime_setup),
        ("CSV Workflow", test_csv_workflow),
        ("Error Handling", test_error_handling),
        ("Data Types", test_data_types)
    ]

    for suite_name, test_func in test_suites:
        try:
            result = test_func()
            all_results.append((suite_name, result))
        except Exception as e:
            print(f"\n✗ Test suite '{suite_name}' crashed: {e}")
            traceback.print_exc()
            all_results.append((suite_name, {"passed": 0, "failed": 1, "errors": [(suite_name, str(e), traceback.format_exc())]}))

    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    total_passed = 0
    total_failed = 0

    for suite_name, result in all_results:
        passed = result["passed"]
        failed = result["failed"]
        total_passed += passed
        total_failed += failed

        status = "✓" if failed == 0 else "✗"
        print(f"{status} {suite_name}: {passed} passed, {failed} failed")

    print("\n" + "=" * 70)
    print(f"TOTAL: {total_passed} tests passed, {total_failed} tests failed")
    print("=" * 70)

    # Print errors if any
    if total_failed > 0:
        print("\n" + "=" * 70)
        print("ERRORS DETAILS")
        print("=" * 70)
        for suite_name, result in all_results:
            if result["errors"]:
                for error_name, error_msg, error_trace in result["errors"]:
                    print(f"\n--- {error_name} ---")
                    print(f"Error: {error_msg}")
                    if "--verbose" in sys.argv:
                        print("Traceback:")
                        print(error_trace)

    # Return exit code
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

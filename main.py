#!/usr/bin/env python3
"""
Mutual Fund Analysis Multi-Agent System
========================================

This application uses Google's ADK (Agent Development Kit) to create a multi-agent
system for analyzing mutual funds. It coordinates four specialized agents:

1. Yahoo Finance Agent - Fetches financial data
2. CSV Data Agent - Processes CSV files
3. Google Search Agent - Searches for information
4. Code Execution Agent - Performs calculations and analysis
"""

import os
from google.adk.runtime import Runtime
from agents.coordinator import coordinator_agent


def main():
    """Run the multi-agent system."""
    print("=" * 70)
    print("Mutual Fund Analysis Multi-Agent System")
    print("=" * 70)
    print("\nInitialized with 4 specialized agents:")
    print("  1. Yahoo Finance Agent - Real-time financial data")
    print("  2. CSV Data Agent - File operations and analysis")
    print("  3. Google Search Agent - Web search capabilities")
    print("  4. Code Execution Agent - Python code execution")
    print("\nCoordinator Agent will orchestrate all agents to answer your queries.")
    print("=" * 70)
    print()

    # Create runtime configuration
    runtime = Runtime(root_agent=coordinator_agent)

    # Interactive mode
    print("Enter your queries (type 'quit', 'exit', or 'q' to stop):\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using the Mutual Fund Analysis System!")
                break

            if not user_input:
                continue

            print("\nAgent: ", end="", flush=True)

            # Run the agent
            response = runtime.run(user_input)

            # Print the response
            print(response.text)
            print()

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.\n")


def run_example_queries():
    """Run some example queries to demonstrate the system."""
    runtime = Runtime(root_agent=coordinator_agent)

    example_queries = [
        "List all CSV files in the current directory",
        "Read the sample_mutual_funds.csv file and give me a summary",
        "What are the top 3 funds by 1 Year Return in the sample data?",
        "Search for recent news about mutual fund investments",
        "Get the current price of VTSAX mutual fund"
    ]

    print("Running example queries...\n")

    for i, query in enumerate(example_queries, 1):
        print(f"\n{'='*70}")
        print(f"Example Query {i}: {query}")
        print('='*70)

        try:
            response = runtime.run(query)
            print(f"\nResponse:\n{response.text}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    import sys

    # Check if user wants to run examples
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        run_example_queries()
    else:
        main()

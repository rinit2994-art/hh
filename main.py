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

REQUIREMENTS:
- Set GOOGLE_API_KEY environment variable for Google AI API, OR
- Configure Google Cloud with project and location for Vertex AI
"""

import os
import sys
import uuid
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.coordinator import coordinator_agent


def check_credentials():
    """Check if API credentials are configured."""
    has_api_key = bool(os.getenv('GOOGLE_API_KEY'))
    has_cloud = bool(os.getenv('GOOGLE_CLOUD_PROJECT'))

    if not has_api_key and not has_cloud:
        print("⚠️  WARNING: No Google API credentials found!")
        print("\nTo use the multi-agent system, you need one of:")
        print("\n1. Google AI API (recommended for testing):")
        print("   export GOOGLE_API_KEY='your-api-key'")
        print("\n2. Google Cloud Vertex AI:")
        print("   export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("   export GOOGLE_CLOUD_LOCATION='us-central1'")
        print("   # Then authenticate: gcloud auth application-default login")
        print("\n" + "=" * 70)
        print("\nAlternatives without API keys:")
        print("- Run 'python demo.py' to see agent capabilities")
        print("- Use individual agent tools programmatically")
        print("- Run 'python comprehensive_test.py' to verify functionality")
        print("=" * 70 + "\n")
        return False

    return True


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

    # Check for API credentials
    if not check_credentials():
        return 1

    try:
        # Create session service
        session_service = InMemorySessionService()

        # Create runner with coordinator agent
        runner = Runner(
            app_name="mutual_fund_analyzer",
            agent=coordinator_agent,
            session_service=session_service
        )

        # Create a session
        session_id = str(uuid.uuid4())
        user_id = "user"

        # Create session in session service
        session_service.create_session_sync(
            app_name="mutual_fund_analyzer",
            user_id=user_id,
            session_id=session_id
        )

        print(f"✓ System ready! Session ID: {session_id[:8]}...\n")

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

                # Create message
                message = types.Content(
                    role="user",
                    parts=[types.Part(text=user_input)]
                )

                print("\nAgent: ", end="", flush=True)

                # Run the agent and collect events
                events = runner.run(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=message
                )

                # Process and display events
                response_text = []
                for event in events:
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    response_text.append(part.text)

                if response_text:
                    print(' '.join(response_text))
                else:
                    print("(No response generated)")
                print()

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.\n")

        return 0

    except Exception as e:
        print(f"\n✗ Failed to initialize system: {e}")
        import traceback
        traceback.print_exc()
        return 1


def run_example_queries():
    """Run some example queries to demonstrate the system."""
    if not check_credentials():
        print("\nNote: Example queries require API credentials.")
        print("Run 'python demo.py' instead for offline demonstrations.\n")
        return 1

    try:
        # Create session service
        session_service = InMemorySessionService()

        # Create runner
        runner = Runner(
            app_name="mutual_fund_analyzer",
            agent=coordinator_agent,
            session_service=session_service
        )

        # Create session
        session_id = str(uuid.uuid4())
        user_id = "example_user"

        session_service.create_session_sync(
            app_name="mutual_fund_analyzer",
            user_id=user_id,
            session_id=session_id
        )

        example_queries = [
            "List all CSV files in the current directory",
            "Read the sample_mutual_funds.csv file and give me a summary",
            "What are the top 3 funds by 1 Year Return in the sample data?",
        ]

        print("Running example queries...\n")

        for i, query in enumerate(example_queries, 1):
            print(f"\n{'='*70}")
            print(f"Example Query {i}: {query}")
            print('='*70)

            try:
                message = types.Content(
                    role="user",
                    parts=[types.Part(text=query)]
                )

                events = runner.run(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=message
                )

                response_text = []
                for event in events:
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    response_text.append(part.text)

                if response_text:
                    print(f"\nResponse:\n{' '.join(response_text)}\n")
                else:
                    print("\n(No response generated)\n")

            except Exception as e:
                print(f"\nError: {e}\n")

        return 0

    except Exception as e:
        print(f"\n✗ Failed to run examples: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Check if user wants to run examples
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        sys.exit(run_example_queries())
    else:
        sys.exit(main())

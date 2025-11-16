#!/usr/bin/env python3
"""Test ADK Runner with proper usage."""

import uuid
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.coordinator import coordinator_agent


def test_runner_basic():
    """Test basic runner functionality."""
    print("Testing ADK Runner...")

    try:
        # Create session service
        session_service = InMemorySessionService()

        # Create runner
        runner = Runner(
            app_name="mutual_fund_test",
            agent=coordinator_agent,
            session_service=session_service
        )
        print("✓ Runner created successfully")

        # Create a session
        session_id = str(uuid.uuid4())
        user_id = "test_user"

        # Create the session in the session service
        session_service.create_session_sync(
            app_name="mutual_fund_test",
            user_id=user_id,
            session_id=session_id
        )
        print(f"✓ Session created: {session_id}")

        # Create a message
        message = types.Content(
            role="user",
            parts=[types.Part(text="List CSV files in current directory")]
        )

        print(f"\nTesting with query: '{message.parts[0].text}'")

        # Run the agent
        events = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        )

        # Process events
        print("\nProcessing events:")
        for event in events:
            print(f"  Event type: {type(event).__name__}")
            if hasattr(event, 'content'):
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text'):
                            print(f"    Text: {part.text[:100]}")

        print("\n✓ Query executed successfully!")
        return True

    except Exception as e:
        print(f"\n✗ Runner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_runner_basic()
    exit(0 if success else 1)

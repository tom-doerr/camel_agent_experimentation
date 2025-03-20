from camel.messages import BaseMessage

# Fix import path for examples
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# pylint: disable=import-error
from examples.demo_tool_usage import GreetingTool, setup_tool_agent


def test_tool_usage_agent():
    """Test that the agent can use a simple greeting tool."""
    # Setup
    agent = setup_tool_agent()

    # Test execution
    user_msg = BaseMessage.make_user_message(
        role_name="User", content="Use the greeting tool to say hello"
    )
    response = agent.step(user_msg)

    # Verify tool usage
    assert "Hello from tool!" in response.content, "Tool output not found in response"
    assert "greeting_tool" in response.content, "Tool name not mentioned in response"


class TestGreetingTool:  # pylint: disable=too-few-public-methods
    """Test suite for the GreetingTool functionality."""

    def test_tool_execution(self):
        """Test basic tool execution."""
        tool = GreetingTool()
        result = tool.execute()
        assert result == "Hello from tool!", "Incorrect tool output"

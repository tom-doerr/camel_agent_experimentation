import sys
import os

# Add project root and examples directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from examples.demo_tool_usage import GreetingTool, setup_tool_agent
from examples.messages import BaseMessage


def test_tool_presence():
    """Test that the agent is initialized with the correct tool."""
    agent = setup_tool_agent()
    assert "greeting_tool" in agent.tools, "Greeting tool not registered"


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

    # Verify tool registration in agent
    assert "greeting_tool" in agent.tools, "Tool not registered with agent"


def test_non_tool_usage_response():
    """Test agent response when no tool is needed"""
    agent = setup_tool_agent()
    user_msg = BaseMessage.make_user_message(
        role_name="User", content="Just say hello normally"
    )
    response = agent.step(user_msg)
    assert "understanding" in response.content.lower(), "Should show default response"
    assert "greeting_tool" not in response.content, "Should not mention tools"


class TestGreetingTool:
    def test_tool_properties(self):
        """Test tool metadata."""
        tool = GreetingTool()
        assert tool.name == "greeting_tool"
        assert "friendly greeting" in tool.description

    def test_tool_execution(self):
        """Test basic tool execution."""
        tool = GreetingTool()
        result = tool.execute()
        assert result == "Hello from tool!", "Incorrect tool output"

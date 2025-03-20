import pytest
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from examples.demo_tool_usage import GreetingTool, setup_tool_agent

def test_tool_usage_agent():
    """Test that the agent can use a simple greeting tool."""
    # Setup
    agent = setup_tool_agent()
    
    # Test execution
    user_msg = BaseMessage.make_user_message(
        role_name="User",
        content="Use the greeting tool to say hello"
    )
    response = agent.step(user_msg)
    
    # Verify tool usage
    assert "Hello from tool!" in response.content, "Tool output not found in response"
    assert "greeting_tool" in response.content, "Tool name not mentioned in response"

class TestGreetingTool:
    """Test suite for the GreetingTool functionality."""
    
    def test_tool_execution(self):
        """Test basic tool execution."""
        tool = GreetingTool()
        result = tool.execute()
        assert result == "Hello from tool!", "Incorrect tool output"

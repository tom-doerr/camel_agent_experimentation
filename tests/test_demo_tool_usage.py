import sys
import os

# Add project root and examples directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
examples_dir = os.path.join(project_root, "examples")
sys.path.insert(0, project_root)
sys.path.insert(0, examples_dir)

# pylint: disable=no-name-in-module,import-error
from examples.demo_tool_usage import (
    GreetingTool,
    TextRatingTool,
    DiskUsageTool,
    setup_tool_agent,
    ChatAgent,
    ChatHistoryMemory,
)
from examples.messages import BaseMessage


def test_tool_presence():
    """Test that the agent is initialized with the correct tools."""
    agent = setup_tool_agent()
    assert "greeting_tool" in agent.tools, "Greeting tool not registered"
    assert "rating_tool" in agent.tools, "Rating tool not registered"


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

    # Verify self-reflection is stored in memory
    assert (
        len(agent.memory.messages) >= 2
    ), "Should have at least user message and response"
    last_msg = agent.memory.messages[-1]
    assert "greeting_tool" in last_msg.content, "Tool name should be in memory"
    assert (
        "Used greeting_tool" in last_msg.content
    ), "Action should be recorded in memory"


def test_non_tool_usage_response_with_sufficient_input():
    """Test agent response when input has enough context"""
    agent = setup_tool_agent()
    user_msg = BaseMessage.make_user_message(
        role_name="User", content="Just say hello normally"
    )
    response = agent.step(user_msg)
    assert "Hello World!" in response.content, "Should show hello world response"
    assert "greeting_tool" not in response.content, "Should not mention tools"

def test_agent_requests_missing_context():
    """Test agent asks for help when missing context"""
    agent = setup_tool_agent()
    user_msg = BaseMessage.make_user_message(
        role_name="User", content="Hi"
    )
    response = agent.step(user_msg)
    assert "more details" in response.content.lower(), "Should request more context"
    assert "?" in response.content, "Should phrase as question"


def test_multi_step_conversation():
    """Test agent maintains conversation history across steps"""
    agent = setup_tool_agent()

    # First message with tool usage
    msg1 = BaseMessage.make_user_message("User", "Use greeting tool")
    response1 = agent.step(msg1)

    # Second message without tool
    msg2 = BaseMessage.make_user_message("User", "Now just say hi")
    response2 = agent.step(msg2)

    # Verify both messages and responses are in memory
    assert (
        len(agent.memory.messages) == 5
    ), "Should have 2 user messages + 2 responses + 1 system reflection"
    assert "Hello from tool!" in response1.content
    assert "Hello World!" in response2.content


def test_agent_initialization():
    """Test basic agent creation with empty tools"""
    memory = ChatHistoryMemory(window_size=5)
    agent = ChatAgent(memory=memory, tools=[])
    assert isinstance(agent, ChatAgent), "Should create ChatAgent instance"
    assert len(agent.tools) == 0, "Agent should have no tools by default"


class TestTextRatingTool:
    def test_tool_properties(self):
        """Test rating tool metadata."""
        tool = TextRatingTool()
        assert tool.name == "rating_tool"
        assert "text complexity" in tool.description

    def test_tool_execution(self):
        """Test basic rating tool execution."""
        tool = TextRatingTool()
        result = tool.execute("Sample text")
        assert "Rating:" in result
        assert "/10" in result


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


class TestDiskUsageTool:
    def test_tool_properties(self):
        """Test disk usage tool metadata."""
        tool = DiskUsageTool()
        assert tool.name == "disk_usage_tool"
        assert "disk space" in tool.description.lower()

    def test_tool_execution(self):
        """Test disk usage tool execution."""
        tool = DiskUsageTool()
        result = tool.execute()
        assert "Total" in result
        assert "Used" in result
        assert "Free" in result
        assert "%" in result

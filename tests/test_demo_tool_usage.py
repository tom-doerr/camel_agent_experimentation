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
    user_msg = BaseMessage.make_user_message(role_name="User", content="Hi")
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

    # Verify message sequence and types
    message_types = [msg.role_type for msg in agent.memory.messages]
    assert message_types[:5] == [
        "user",
        "system",
        "system",
        "system",
        "assistant",
    ], f"Unexpected message sequence start: {message_types}"

    # Verify response content
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


class TestEndToEndAgentInterface:
    """End-to-end tests for core agent interface behavior"""

    def __init__(self):
        """Initialize test case"""
        super().__init__()
        self.agent = None

    def setup_method(self):
        """Fresh agent for each test (pytest setup convention)"""
        self.agent = setup_tool_agent()

    def assert_tool_used(self, response, tool_name):
        """Verify tool usage in response"""
        assert tool_name in response.content, f"{tool_name} not mentioned"
        assert "Used" in response.content, "Tool usage not recorded"

    def test_full_conversation_flow(self):
        """Test complete conversation with multiple tool usages"""
        # Start conversation
        user_msg1 = BaseMessage.make_user_message(
            "User", "Can you use greeting_tool and disk_usage_tool?"
        )
        response1 = self.agent.step(user_msg1)

        # Verify combined tool responses
        self.assert_tool_used(response1, "greeting_tool")
        self.assert_tool_used(response1, "disk_usage_tool")
        assert "GB" in response1.content, "GB units not displayed"

        # Follow-up request
        user_msg2 = BaseMessage.make_user_message(
            "User", "Now rate the complexity of this text: 'The quick brown fox'"
        )
        response2 = self.agent.step(user_msg2)

        # Verify rating tool response
        self.assert_tool_used(response2, "rating_tool")
        assert "Rating:" in response2.content, "Rating not shown"
        assert "/10" in response2.content, "10-point scale missing"

    def test_multi_tool_response_flow(self):
        """Test agent can combine multiple tool responses in one message"""
        user_msg = BaseMessage.make_user_message(
            "User",
            "Use greeting_tool, disk_usage_tool and rating_tool on: 'Sample text'",
        )
        response = self.agent.step(user_msg)

        # Verify all tools responded
        self.assert_tool_used(response, "greeting_tool")
        self.assert_tool_used(response, "disk_usage_tool")
        self.assert_tool_used(response, "rating_tool")

    def test_delegation_workflow(self):
        """Test full delegation workflow between agents"""
        memory = ChatHistoryMemory()
        worker = ChatAgent(memory=memory, tools=[GreetingTool])
        manager = ChatAgent(memory=memory, tools=[], delegate_workers=[worker])

        # Send delegation request
        task = BaseMessage.make_user_message(
            "Manager", "Delegate to worker: use greeting tool"
        )
        response = manager.step(task)

        # Verify response chain
        assert "Hello from tool!" in response.content
        assert "delegated" in response.content.lower()

        # Verify memory contains full workflow traces
        roles_present = {msg.role_type for msg in memory.messages}
        assert "system" in roles_present, "Missing system messages"
        assert "assistant" in roles_present, "Missing assistant responses"

    def test_tool_usage_response_flow(self):
        """Test complete flow from user message to tool usage response"""
        agent = setup_tool_agent()
        user_msg = BaseMessage.make_user_message(
            "User",
            "Please use disk_usage_tool and rating_tool on: 'The quick brown fox'",
        )
        response = agent.step(user_msg)

        # Verify response contains both tool outputs
        assert "disk_usage_tool" in response.content
        assert "GB" in response.content
        assert "rating_tool" in response.content
        assert "/10" in response.content

        # Verify memory contains all message types
        message_types = {msg.role_type for msg in agent.memory.messages}
        assert message_types == {
            "user",
            "assistant",
            "system",
        }, "Missing expected message types in memory"

    def test_mixed_conversation_flow(self):
        """Test interaction mixing tool usage and natural responses"""
        agent = setup_tool_agent()

        # First message with tool request
        tool_msg = BaseMessage.make_user_message("User", "Use greeting_tool")
        tool_response = agent.step(tool_msg)
        assert "Hello from tool!" in tool_response.content

        # Second message with natural request
        natural_msg = BaseMessage.make_user_message("User", "Now just say hello")
        natural_response = agent.step(natural_msg)
        assert "Hello World!" in natural_response.content

        # Verify message sequence
        message_sequence = [msg.role_type for msg in agent.memory.messages]
        assert message_sequence == [
            "user",
            "system",
            "assistant",  # First interaction
            "user",
            "assistant",  # Second interaction
        ], "Incorrect message sequence after mixed conversation"

    def test_error_handling_flow(self):
        """Test agent response to invalid requests and error metadata"""
        agent = setup_tool_agent()
        user_msg = BaseMessage.make_user_message("User", "Do something impossible")
        response = agent.step(user_msg)

        # Verify fallback response
        assert "Hello World!" in response.content
        # Should record error in system messages
        assert any(
            msg.role_type == "system" and "error" in msg.content.lower()
            for msg in agent.memory.messages
        ), "Missing error system message"

    def test_agent_memory_control(self):
        """Test agent can decide when to update memory"""
        agent = setup_tool_agent()
        
        # First message with instruction to not store
        msg1 = BaseMessage.make_user_message("User", "Remember this secret: 12345 [DO NOT STORE]")
        response1 = agent.step(msg1)
        
        # Verify message was processed but not stored
        assert "12345" in response1.content
        assert not any("12345" in msg.content for msg in agent.memory.messages)

        # Second message with normal storage
        msg2 = BaseMessage.make_user_message("User", "Remember this public: 67890")
        response2 = agent.step(msg2)
        
        # Verify message was stored
        assert "67890" in response2.content
        assert any("67890" in msg.content for msg in agent.memory.messages)

    def test_agent_memory_filtering(self):
        """Test agent can filter what gets stored in memory"""
        agent = setup_tool_agent()
        
        # Send message with mixed content
        msg = BaseMessage.make_user_message(
            "User", 
            "Private: 12345, Public: 67890 [STORE ONLY PUBLIC]"
        )
        agent.step(msg)
        
        # Verify memory contains only public data
        memory_content = " ".join(msg.content for msg in agent.memory.messages)
        assert "67890" in memory_content
        assert "12345" not in memory_content

    def test_agent_memory_summarization(self):
        """Test agent can summarize instead of storing verbatim"""
        agent = setup_tool_agent()
        
        # Send long message
        long_text = " ".join(["foo"] * 50)
        msg = BaseMessage.make_user_message("User", f"{long_text} [SUMMARIZE]")
        agent.step(msg)
        
        # Verify memory contains summary
        assert any(
            "summary" in msg.content.lower() and len(msg.content) < 50
            for msg in agent.memory.messages
        ), "Memory should contain summarized version"


class TestDelegation:
    """Test agent-to-agent delegation"""

    def test_agent_creation_with_delegation(self):
        """Test agent can be initialized with delegation ability"""
        memory = ChatHistoryMemory()
        worker = ChatAgent(memory=memory, tools=[])
        manager = ChatAgent(memory=memory, tools=[], delegate_workers=[worker])

        assert hasattr(manager, "delegate_workers"), "Manager should have workers list"
        assert len(manager.delegate_workers) == 1, "Manager should have 1 worker"
        assert isinstance(
            manager.delegate_workers[0], ChatAgent
        ), "Worker should be agent"

    def test_simple_delegation(self):
        """Test manager can delegate task to worker"""
        memory = ChatHistoryMemory()
        worker = ChatAgent(memory=memory, tools=[GreetingTool])  # Pass class reference
        manager = ChatAgent(memory=memory, tools=[], delegate_workers=[worker])

        task = BaseMessage.make_user_message(
            "Manager", "Delegate to worker: use greeting tool"
        )
        response = manager.step(task)

        assert "Hello from tool!" in response.content, "Worker should handle task"
        assert (
            "delegated to worker" in response.content.lower()
        ), "Should mention delegation"

    def test_subtask_delegation_with_feedback(self):
        """Test delegated subtask response is stored in manager memory"""
        memory = ChatHistoryMemory()
        worker = ChatAgent(memory=memory, tools=[GreetingTool])
        manager = ChatAgent(memory=memory, tools=[], delegate_workers=[worker])

        task = BaseMessage.make_user_message(
            "Manager", "Delegate to worker: use greeting tool"
        )
        manager.step(task)

        # Verify both delegation and tool response are in memory
        assert (
            len(memory.messages) >= 3
        ), "Should have task, delegation, and tool response"
        assert any(
            "Delegated to worker" in msg.content for msg in memory.messages
        ), "Missing delegation record"
        assert any(
            "Hello from tool" in msg.content for msg in memory.messages
        ), "Missing tool result in memory"

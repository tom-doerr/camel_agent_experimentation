from typing import Any, List, Optional
import shutil
from examples.messages import BaseMessage


# pylint: disable=too-few-public-methods
class ChatHistoryMemory:
    """Memory implementation with storage control"""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.messages: List[BaseMessage] = []

    def should_store(self, message: BaseMessage) -> bool:
        """Determine if message should be stored"""
        # Default implementation - agents can override
        if "[DO NOT STORE]" in message.content:
            return False
        if "[STORE ONLY PUBLIC]" in message.content:
            return "Public:" in message.content
        return True

    def add_message(self, message: BaseMessage) -> None:
        """Add message to memory if it passes filters"""
        if self.should_store(message):
            self.messages.append(message)
            if len(self.messages) > self.window_size:
                self.messages.pop(0)


# pylint: disable=too-few-public-methods
class ChatAgent:
    """Minimal agent implementation with tool support"""

    def __init__(
        self,
        memory: ChatHistoryMemory,
        tools: List[Any],
        delegate_workers: List[Any] = None,
    ):
        """Initialize a ChatAgent with shared memory capability
        
        Args:
            memory: ChatHistoryMemory instance (can be shared between agents)
            tools: List of tool classes to register
            delegate_workers: List of ChatAgents to delegate to
        """
        self.memory = memory
        # Store tools by name with class references
        self.tools = {tool.name: tool for tool in tools}
        self.delegate_workers = delegate_workers or []

    def step(self, message: BaseMessage) -> BaseMessage:
        """Process a message and return response"""
        self.memory.add_message(message)

        # Check for delegation commands first
        if "delegate to" in message.content.lower():
            for worker in self.delegate_workers:
                # Pass the task directly to worker agent
                worker_response = worker.step(message)
                response = BaseMessage(
                    "Assistant",
                    f"Delegated to worker: {worker_response.content}",
                    role_type="assistant",
                )
                self.memory.add_message(response)
                return response

        # Check if any tool name is mentioned in the message
        content_lower = message.content.lower()
        tool_responses = []

        # Collect all exact tool matches first
        for tool_name, tool_cls in self.tools.items():
            if tool_name in content_lower:
                tool_response = tool_cls().execute(message.content)
                tool_responses.append(f"Used {tool_name}: {tool_response}")
                self.memory.add_message(
                    BaseMessage(
                        "System",
                        f"Agent used {tool_name}: {tool_response}",
                        role_type="system",
                    )
                )

        # If no exact matches, check for partial matches
        if not tool_responses:
            for tool_name, tool_cls in self.tools.items():
                if any(part in content_lower for part in tool_name.split("_")):
                    tool_response = tool_cls().execute(message.content)
                    tool_responses.append(f"Used {tool_name}: {tool_response}")
                    self.memory.add_message(
                        BaseMessage(
                            "System",
                            f"Agent used {tool_name}: {tool_response}",
                            role_type="system",
                        )
                    )

        if tool_responses:
            response = BaseMessage(
                "Assistant",
                "\n".join(tool_responses),
                role_type="assistant",
            )
            self.memory.add_message(response)
            return response

        # Handle errors and missing context
        try:
            if len(message.content.strip()) < 5:
                raise ValueError("Insufficient context")

            response = BaseMessage("Assistant", "Hello World!", role_type="assistant")

        except ValueError as e:  # More specific exception
            self.memory.add_message(
                BaseMessage(
                    "System",
                    f"Error processing request: {str(e)}",
                    role_type="system",
                )
            )
            response = BaseMessage(
                "Assistant",
                "Could you please provide more details about your request?",
                role_type="assistant",
            )

        self.memory.add_message(response)
        return response


class BaseTool:
    """Base tool interface"""

    name: str
    description: str

    def execute(self, *args, **kwargs) -> str:
        raise NotImplementedError


class TextRatingTool(
    BaseTool
):  # pylint: disable=too-few-public-methods,abstract-method
    """Tool that analyzes text complexity and provides a rating."""

    name: str = "rating_tool"
    description: str = "Useful for rating text complexity from 1-10 based on length"

    def execute(self, *args: str, **kwargs: str) -> str:
        """Analyze text and return a rating."""
        text = args[0] if args else ""
        word_count = len(text.split())
        rating = min(word_count // 10, 10)  # 1 point per 10 words up to 100
        return f"Rating: {rating}/10 (based on {word_count} words)"


class DiskUsageTool(BaseTool):  # pylint: disable=too-few-public-methods,abstract-method
    """Tool that checks disk usage statistics.

    Attributes:
        name: The name of the tool displayed to the agent
        description: Help text for when to use this tool
    """

    name: str = "disk_usage_tool"
    description: str = "Useful for checking disk space usage and available capacity"

    def execute(
        self, *args: str, **kwargs: str
    ) -> str:  # pylint: disable=unused-argument
        """Execute the disk usage check and return formatted statistics."""
        usage = shutil.disk_usage("/")
        percent_used = (usage.used / usage.total) * 100
        return (
            f"Disk Usage: {percent_used:.1f}% used\n"
            f"Total: {usage.total // (1024**3)}GB, "
            f"Used: {usage.used // (1024**3)}GB, "
            f"Free: {usage.free // (1024**3)}GB"
        )


class GreetingTool(BaseTool):  # pylint: disable=too-few-public-methods,abstract-method
    """Tool that returns a fixed greeting message.

    Attributes:
        name: The name of the tool displayed to the agent
        description: Help text for the agent about when to use this tool
    """

    name: str = "greeting_tool"
    description: str = "Useful for when you need to generate a friendly greeting"

    def execute(
        self, *args: str, **kwargs: str
    ) -> str:  # pylint: disable=unused-argument
        """Execute the greeting tool and return a fixed message."""
        return "Hello from tool!"


def setup_tool_agent() -> ChatAgent:
    """Initialize and configure a ChatAgent with greeting tool support.

    Returns:
        ChatAgent: Agent configured with greeting tool and memory
    """
    memory = ChatHistoryMemory(window_size=10)
    return ChatAgent(memory=memory, tools=[GreetingTool, TextRatingTool, DiskUsageTool])


def cli_main(input_str: Optional[str] = None) -> str:
    """Entry point for CLI execution"""
    agent = setup_tool_agent()
    if input_str:
        msg = BaseMessage.make_user_message(role_name="User", content=input_str)
        response = agent.step(msg)
        return response.content
    return ""


if __name__ == "__main__":
    print("Demo: CAMEL Agent Tool Usage")
    user_input = BaseMessage.make_user_message(
        role_name="User", content="Please use the greeting tool to say hello"
    )
    demo_response = cli_main(user_input.content)
    print(f"\nAgent Response:\n{demo_response}")

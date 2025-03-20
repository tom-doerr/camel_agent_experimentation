from typing import Any, List
from examples.messages import BaseMessage


# pylint: disable=too-few-public-methods
class ChatHistoryMemory:
    """Minimal memory implementation"""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.messages: List[BaseMessage] = []

    def add_message(self, message: BaseMessage) -> None:
        """Add message to memory"""
        self.messages.append(message)
        if len(self.messages) > self.window_size:
            self.messages.pop(0)


# pylint: disable=too-few-public-methods
class ChatAgent:
    """Minimal agent implementation with tool support"""

    def __init__(self, memory: ChatHistoryMemory, tools: List[Any]):
        self.memory = memory
        # Store tools by name with class references
        self.tools = {tool.name: tool for tool in tools}

    def step(self, message: BaseMessage) -> BaseMessage:
        """Process a message and return response"""
        self.memory.add_message(message)

        # Check if any tool name is mentioned in the message
        content_lower = message.content.lower()
        for tool_name, tool_cls in self.tools.items():
            # Split tool name into parts and check if any are in the message
            if any(part in content_lower for part in tool_name.split("_")):
                tool_response = tool_cls().execute()
                response = BaseMessage(
                    "Assistant",
                    f"Used {tool_name}: {tool_response}",
                    role_type="assistant",
                )
                self.memory.add_message(response)
                return response

        response = BaseMessage("Assistant", "Hello World!", role_type="assistant")
        self.memory.add_message(response)
        return response


class BaseTool:
    """Base tool interface"""

    name: str
    description: str

    def execute(self, *args, **kwargs) -> str:
        raise NotImplementedError


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
    return ChatAgent(memory=memory, tools=[GreetingTool])


if __name__ == "__main__":
    demo_agent = setup_tool_agent()
    print("Demo: CAMEL Agent Tool Usage")
    user_input = BaseMessage.make_user_message(
        role_name="User", content="Please use the greeting tool to say hello"
    )
    demo_response = demo_agent.step(user_input)
    print(f"\nAgent Response:\n{demo_response.content}")

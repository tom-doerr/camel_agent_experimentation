from camel.agents import ChatAgent
from camel.memories import ChatHistoryMemory  # Corrected import path
from camel.models import ModelFactory
from camel.messages import BaseMessage
from camel.tools.base_tool import BaseTool  # Corrected import path


class GreetingTool(BaseTool):  # pylint: disable=too-few-public-methods
    """Tool that returns a fixed greeting message.
    
    Attributes:
        name: The name of the tool displayed to the agent
        description: Help text for the agent about when to use this tool
    """

    name: str = "greeting_tool"
    description: str = "Useful for when you need to generate a friendly greeting"

    def execute(self, *args: str, **kwargs: str) -> str:  # pylint: disable=unused-argument
        """Execute the greeting tool and return a fixed message."""
        return "Hello from tool!"


def setup_tool_agent() -> ChatAgent:
    """Initialize and configure a ChatAgent with greeting tool support.
    
    Returns:
        ChatAgent: Agent configured with greeting tool and memory
    """
    memory = ChatHistoryMemory(window_size=10)
    model = ModelFactory.create(
        model_platform="openai",
        model_type="gpt-4",
        model_config_dict={"api_key": "sk-test-key"},  # Correct parameter name
    )
    return ChatAgent(model=model, memory=memory, tools=[GreetingTool()])


if __name__ == "__main__":
    demo_agent = setup_tool_agent()
    print("Demo: CAMEL Agent Tool Usage")
    user_input = BaseMessage.make_user_message(
        role_name="User", content="Please use the greeting tool to say hello"
    )
    response = demo_agent.step(user_input)
    print(f"\nAgent Response:\n{response.content}")

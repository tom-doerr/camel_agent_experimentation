from camel.agents import ChatAgent
from camel.agents.memory import ChatHistoryMemory
from camel.models import ModelFactory
from camel.messages import BaseMessage
from camel.agents.tools import BaseTool


class GreetingTool(BaseTool):
    """Tool that returns a fixed greeting message.

    Attributes:
        name (str): The name of the tool displayed to the agent
        description (str): Help text for the agent about when to use this tool
    """

    name = "greeting_tool"
    description = "Useful for when you need to generate a friendly greeting"

    def execute(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Execute the greeting tool."""
        return "Hello from tool!"


def setup_tool_agent():
    """Set up and return a ChatAgent configured with tools."""
    memory = ChatHistoryMemory(window_size=10)
    model = ModelFactory.create(
        model_platform="openai",
        model_config_dict={"api_key": "sk-test-key", "model": "gpt-4"},
    )
    agent = ChatAgent(model=model, memory=memory, tools=[GreetingTool()])
    return agent


if __name__ == "__main__":
    demo_agent = setup_tool_agent()
    print("Demo: CAMEL Agent Tool Usage")
    user_input = BaseMessage.make_user_message(
        role_name="User", content="Please use the greeting tool to say hello"
    )
    response = demo_agent.step(user_input)
    print(f"\nAgent Response:\n{response.content}")

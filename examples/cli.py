"""Command line interface for interacting with the agent"""

import click
from .demo_tool_usage import setup_tool_agent, ChatAgent
from .messages import BaseMessage


def process_message(agent: ChatAgent, message: str, verbose: bool = False) -> str:
    """Process a single message through the agent"""
    user_msg = BaseMessage.make_user_message(role_name="User", content=message)
    response = agent.step(user_msg)

    output = f"Agent: {response.content}"
    if verbose:
        output += f"\n[System reflection] {agent.memory.messages[-1].content}"
    return output


@click.command()
@click.option("--message", "-m", help="Direct message to send")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed processing information")
def main(message, verbose):
    """Chat with an AI agent - Choose a message or interactive mode"""
    agent = setup_tool_agent()

    if message:
        click.echo(process_message(agent, message, verbose))
    else:
        click.echo("How can I help you?")
        while True:
            try:
                message = input("> ")
                if message.lower() in ["exit", "quit"]:
                    break
                print(process_message(agent, message, verbose))
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()

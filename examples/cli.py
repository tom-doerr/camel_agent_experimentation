"""Command line interface for interacting with the agent"""

import click
from .demo_tool_usage import setup_tool_agent, ChatAgent
from .messages import BaseMessage


def process_message(agent: ChatAgent, message: str, verbose: bool = False) -> str:
    """Process a single message through the agent
    
    Args:
        agent: Configured ChatAgent instance
        message: User input message
        verbose: Show system reflections if True
        
    Returns:
        str: Formatted response string
    """
    if not message.strip():
        raise click.UsageError("Received empty message")
    user_msg = BaseMessage.make_user_message(role_name="User", content=message)
    response = agent.step(user_msg)

    output = f"Agent: {response.content}"
    if verbose:
        output += f"\n[System reflection] {agent.memory.messages[-1].content}"
    return output


@click.command()
@click.option("--message", "-m", help="Direct message to send to the agent")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed processing information including system reflections",
)
@click.version_option(version="0.1.0", prog_name="Agent CLI")
def main(message=None, verbose=False):
    """Chat with an AI agent that can use tools

    Run in either direct message mode or interactive conversation mode.

    Examples:

    \b
    $ python -m examples.cli --message "Hello"
    $ python -m examples.cli --verbose --message "Check disk usage"
    """
    agent = setup_tool_agent()

    if message is not None:  # Direct message mode (check for option presence)
        if not message.strip():
            raise click.UsageError("Message cannot be empty when using --message")
        click.echo(process_message(agent, message, verbose))
    else:
        click.echo("How can I help you?")
        while True:
            try:
                message = input("> ")
                if message.lower() in ["exit", "quit"]:
                    break
                print(process_message(agent, message, verbose))
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()

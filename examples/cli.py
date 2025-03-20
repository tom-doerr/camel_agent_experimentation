"""Command line interface for interacting with the agent"""

import argparse
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


def main():
    """Entry point for command line interface"""
    parser = argparse.ArgumentParser(description="Chat with an AI agent")
    parser.add_argument("--message", "-m", help="Direct message to send")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    args = parser.parse_args()
    agent = setup_tool_agent()

    if args.message:
        print(process_message(agent, args.message, args.verbose))
    else:
        print("How can I help you?")
        while True:
            try:
                message = input("> ")
                if message.lower() in ["exit", "quit"]:
                    break
                print(process_message(agent, message, args.verbose))
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()

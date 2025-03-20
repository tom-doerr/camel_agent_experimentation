"""Test command line interface for agent interaction"""

from click.testing import CliRunner
from examples.cli import main


def test_cli_basic_execution():
    """Test basic CLI execution with a message"""
    runner = CliRunner()
    result = runner.invoke(main, ["--message", "Hello"])
    assert "Hello World!" in result.output
    assert result.exit_code == 0


def test_cli_tool_usage():
    """Test CLI execution that triggers a tool"""
    runner = CliRunner()
    result = runner.invoke(main, ["--message", "use greeting tool"])
    assert "Hello from tool!" in result.output 
    assert result.exit_code == 0


def test_cli_verbose_output():
    """Test verbose mode shows additional details"""
    runner = CliRunner()
    result = runner.invoke(main, ["--message", "hi", "--verbose"])
    assert "Hello World!" in result.output
    assert "System reflection" in result.output
    assert result.exit_code == 0


def test_cli_help_output():
    """Test help output shows available options"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "Show this message and exit." in result.output
    assert "--message TEXT" in result.output
    assert "--verbose" in result.output


def test_cli_interactive_mode():
    """Test interactive mode session"""
    runner = CliRunner()
    result = runner.invoke(main, input="Hello\nquit\n")
    assert "How can I help you?" in result.output
    assert "Hello World!" in result.output

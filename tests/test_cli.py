"""Test command line interface for agent interaction"""
from click.testing import CliRunner
from examples import cli, setup_tool_agent

def test_cli_basic_execution():
    """Test basic CLI execution with a message"""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--message", "Hello"])
    assert "Hello World!" in result.output
    assert result.exit_code == 0

def test_cli_tool_usage():
    """Test CLI execution that triggers a tool"""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--message", "use greeting tool"])
    assert "Hello from tool!" in result.output
    assert result.exit_code == 0

def test_cli_verbose_output():
    """Test verbose mode shows additional details"""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--message", "hi", "--verbose"])
    assert "Hello World!" in result.output
    assert "System reflection" in result.output
    assert result.exit_code == 0

def test_cli_interactive_mode(capsys):
    """Test interactive mode session"""
    # Get output and verify responses
    captured = capsys.readouterr()
    assert "How can I help you?" in captured.out
    assert "Rating:" in captured.out

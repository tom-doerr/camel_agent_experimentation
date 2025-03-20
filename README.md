# CAMEL Agent Tool Usage Demo

A minimal implementation of a conversational agent with tool usage capabilities.

## Features

- Basic chat agent with conversation memory
- Tool system integration
- Greeting tool demonstration
- Automated tests for tool usage scenarios

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the demo:
```bash
python examples/demo_tool_usage.py
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
|-- examples/
|   |-- demo_tool_usage.py  # Main agent implementation
|   |-- messages.py         # Base message class
|   `-- __init__.py
|-- tests/
|   `-- test_demo_tool_usage.py  # Integration tests
`-- README.md               # This file
```

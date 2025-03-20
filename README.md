# CAMEL Agent Python Package

### Overview
A properly packaged Python implementation of the CAMEL agent with tool usage capabilities.

## Features

- Proper Python package structure
- Versioned releases
- CLI entry point
- Automated test suite
- Chat agent with conversation memory
- Extensible tool system

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

Run the demo agent:
```bash
camel-agent
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
|-- src/
|   `-- camel_agent/        # Package source code
|       |-- __init__.py
|       |-- cli.py
|       |-- demo_tool_usage.py
|       `-- messages.py
|-- tests/                  # Integration tests
|-- pyproject.toml          # Build configuration
|-- setup.cfg               # Package metadata
`-- README.md               # This file
```

# GenAI Services FastAPI

A workspace for building generative AI services with FastAPI and Streamlit, managed with `uv`.

## Project Structure

```
.
├── src
│   └── genai_services
│       ├── __pycache__
│       ├── part1 # Developing AI Services 
│       ├── part2 # Communicating with External Services
│       ├── __init__.py
│       ├── settings.py # Settings/environment variables for the application
│       ├── tinyllama.py 
│       └── utils.py # Utility functions for the application
├── tests # Tests for the application
│   ├── __init__.py
│   └── test_main.py # Test for the main function
├── AGENTS.md -> CLAUDE.md # Agents documentation for non Claude agents (symlink to CLAUDE.md)
├── CLAUDE.md # Claude definition of the agents (source of truth for the agents)
├── pyproject.toml # Project configuration
├── README.md 
└── uv.lock # Lock file for the project
```

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

## Quick Start

Clone or fork the repository and install the dependencies:

```bash
# Install dependencies
uv sync

# Activate virtual environment (optional)
source .venv/bin/activate

# test the application
uv run pytest
```

## Contributing

Contributions are welcome! Please feel free to submit an issue or a pull request.

You can branch off the `main` branch to make your changes and then submit a pull request to the `main` branch, running the formatting and linting checks with pre-commit hooks.

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit hooks
uv run pre-commit run --all-files
```

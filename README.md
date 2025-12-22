# GenAI Services FastAPI

A workspace for building generative AI services with FastAPI and Streamlit, managed with `uv`.

## Project Structure

```
genai-services-fastapi/
├── src/
│   └── genai_services/     # Main package
│       └── __init__.py
├── tests/                  # Test files
├── pyproject.toml          # Project config & dependencies
└── README.md
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

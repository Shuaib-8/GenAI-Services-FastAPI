# GenAI Services FastAPI

A workspace for building generative AI services with FastAPI and Streamlit, managed with `uv`.

## Project Structure

```
.
├── src
│   └── genai_services
│       ├── __init__.py
│       └── tinyllama.py
├── tests
│   ├── __init__.py
│   └── test_main.py
├── api_main.py
├── bento.py
├── client_st_unified.py
├── models.py
├── pyproject.toml
├── README.md
├── schemas.py
├── utils.py
└── uv.lock
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

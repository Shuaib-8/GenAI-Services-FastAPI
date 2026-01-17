# AGENTS.md

Reference guide for AI coding assistants working with this project.

## Project Identity

**Name**: `genai-services-fastapi`  
**Purpose**: FastAPI workspace for building generative AI services (text, audio, image generation) with Streamlit clients

**Package Name**: `genai_services` (import path for first-party code)  
**Project Root**: Directory containing `pyproject.toml` and `settings.py`

## Tech Stack

- **Python**: 3.11 (strict: `>=3.11,<3.12`)
- **Package Manager**: `uv` (not pip/poetry)
- **Web Framework**: FastAPI with Pydantic
- **ML Stack**: PyTorch, Transformers, Diffusers, Accelerate
- **Integrations**: OpenAI, LangChain, BentoML
- **Quality Tools**: ruff, mypy (strict) or pyrefly, bandit, pre-commit

## Architecture

### Organization Principles

```
src/genai_services/
├── part*/                         # Feature modules (partN directories)
│   ├── api_*.py                  # FastAPI apps (endpoints, routers)
│   ├── models.py                 # ML model loading & inference (if ML-heavy)
│   ├── schemas.py                # Pydantic models for requests/responses
│   ├── dependencies.py           # FastAPI dependency functions
│   ├── client_*.py               # Client code (Streamlit, CLI, etc.)
│   └── project-*/                # Sub-projects (nested modules)
│       ├── api_*.py
│       ├── *.py                  # Domain-specific logic files
│       └── uploads/              # Runtime data directories (gitignored)
├── utils.py                       # Shared utilities (cross-cutting concerns)
└── __init__.py                    # Package entry point
settings.py (root)                 # Pydantic settings (environment config)
```

### File Discovery (for AI agents)

To find relevant files dynamically:
- **API entry points**: Search for `api_*.py` or files with `FastAPI()` instantiation
- **Pydantic models**: Search for `schemas.py` or files with `BaseModel` subclasses
- **ML models**: Search for `models.py` or files with `load_*_model()` functions
- **Settings**: Look for `settings.py` at project root or `BaseSettings` subclasses
- **Utilities**: Check `utils.py` for shared helper functions
- **Tests**: All test files follow `tests/test_*.py` pattern

## Key Patterns

### FastAPI Patterns
- **Model Loading**: Use lifespan context managers to load ML models at startup
- **Model Storage**: Store in module-level `models = {}` dict, access via dict keys
- **State Management**: Models can also be stored in `app.state` for dependency injection
- **Response Types**: Use `StreamingResponse` for audio/images, Pydantic models for JSON

### Pydantic Patterns
- **Type Annotations**: Use `Annotated[type, Field(...)]` for all request/response models
- **Custom Validation**: Use `AfterValidator` for complex validation logic
- **Computed Fields**: Use `@computed_field` for derived properties (e.g., token count)
- **Settings**: Use `pydantic-settings` with `.env` file (look for `BaseSettings` subclasses)

### Async Patterns
- **File Operations**: Always use `aiofiles` for async file I/O
- **HTTP Requests**: Use `httpx.AsyncClient` or `aiohttp.ClientSession` with context managers
- **Concurrent Tasks**: Use `asyncio.gather()` for parallel operations

### ML Model Patterns
- **Device Selection**: Use `accelerator.device` (MPS for Apple Silicon, else CPU)
- **Pipelines**: HuggingFace pipelines for text generation
- **Manual Loading**: `AutoModel` + `AutoProcessor` for audio/custom models

### Logging
- Use `loguru` logger (imported from `loguru import logger`)

## Code Style

- **Line Length**: ruff line length configuration
- **Quotes**: Single quotes for strings
- **Imports**: Sorted with ruff, first-party group = `genai_services`
- **Type Hints**: Required everywhere (pyrefly strict mode enabled)
- **Docstrings**: Simple one-liners for functions

## Navigation & Discovery (for AI Agents)

### Finding Key Components

Use these search strategies instead of hardcoded paths:

```bash
# Find all FastAPI applications
grep -r "FastAPI(" src/ --include="*.py"

# Find all streamlit applications
grep -r "streamlit" src/ --include="*.py"

# Find all Pydantic schemas
grep -r "BaseModel" src/ --include="schemas.py"

# Find settings configuration
find . -name "settings.py" -o -name "*config*.py"

# Find ML model loaders
grep -r "def load_.*_model" src/ --include="*.py"

# Find all API endpoints
grep -r "@app\.(get|post|put|delete)" src/ --include="*.py"

# Find async file operations
grep -r "aiofiles" src/ --include="*.py"
```

### Code Reading Priority

When exploring an unfamiliar module:
1. Start with `api_*.py` → understand endpoints and request flow
2. Check `schemas.py` → understand data models and validation
3. Read `models.py` → understand ML model loading if applicable
4. Check `dependencies.py` → understand shared FastAPI dependencies
5. Review `*.py` domain files → understand business logic

## Essential Commands

```bash
# Dependency management
uv sync                                  # Install all dependencies
uv add <package>                         # Add new package

# Testing & quality
uv run pytest                            # Run all tests
uv run pytest tests/test_*.py -v        # Run specific test pattern
uv run pre-commit run --all-files       # Run all linters

# Individual linters
uv run ruff check .                     # Lint code
uv run ruff format .                    # Format code
uv run pyrefly check .                 # Type check

# Running services (discover via glob: src/**/api_*.py)
uv run fastapi dev <path/to/api_*.py>   # Generic FastAPI dev server
uv run bentoml serve <path/to/bento.py>:<ServiceClass>  # BentoML services
```

## Agent-Specific Guidance

### When Adding New Features

1. **New API Endpoints**
   - Add to appropriate `api_*.py` file (discover via: `find src -name "api_*.py"`)
   - Follow existing patterns (lifespan for models, Pydantic schemas)
   - Use type hints and `Annotated` types

2. **New Pydantic Models**
   - Add to `schemas.py` in the same module (or create if absent)
   - Use `Annotated[type, Field(...)]` pattern
   - Add validation with `AfterValidator` if needed

3. **New ML Models**
   - Loading logic goes in `models.py` (or create if absent)
   - Add to lifespan context manager in API file
   - Store in module-level `models` dict

4. **New Dependencies**
   - Use `uv add <package>` (not pip install)
   - Updates `pyproject.toml` automatically via uv

5. **Environment Variables**
   - Add to settings file (search for `BaseSettings` subclass)
   - Document in `.env.example` if creating

### Common Task Patterns

Rather than fixed references, search for these patterns:

- **File Upload**: Search for `UploadFile` usage or `aiofiles` async file handling
- **Web Scraping**: Search for `aiohttp.ClientSession` or `BeautifulSoup` usage
- **Text Generation**: Search for `generate_text()` or HuggingFace `pipeline()` usage
- **Audio/Image Buffers**: Search for `BytesIO` buffer conversion patterns
- **Async Context Managers**: Search for `@asynccontextmanager` decorator usage

### What to Do

- ✅ Use `uv add <package>` to add new dependencies
- ✅ Use `uv run <command>` to run commands
- ✅ Use `uv run pytest -v` to run tests
- ✅ Use `uv run ruff check .` to lint code
- ✅ Use `uv run ruff format .` to format code
- ✅ Use `uv run pyrefly check .` to type check code
- ✅ Use `uv run pre-commit run --all-files` to run all linters
- ✅ Use `uv run fastapi dev <path/to/api_*.py>` to run the FastAPI development server
- ✅ Use `uv run bentoml serve <path/to/bento.py>:<ServiceClass>` to run the BentoML service
- ✅ Use `uv run streamlit run <path/to/streamlit_app.py>` to run the Streamlit application

### What NOT to Do

- ❌ Don't use `pip install` (use `uv add` or `uv sync`)
- ❌ Don't run Python without `uv run` prefix
- ❌ Don't scatter utility functions (consolidate in `utils.py` or create `*_utils.py`)
- ❌ Don't add dependencies without version constraints
- ❌ Don't use `print()` for logging (use `loguru.logger`)
- ❌ Don't use `open()` for async code (use `aiofiles`)

## Environment Setup

Required environment variables in `.env`:
- `OPENAI_API_KEY` (pattern: `sk-proj-...`)
- Optional: `DATABASE_URL`, `CORS_WHITELIST`, `app_secret`

## Debugging

- VSCode run and debug configurations are in the `.vscode` directory
- Help setup debug configurations in VSCode if needed when running app services in debug mode

## Testing

- Test files: `tests/test_*.py`
- Use pytest fixtures for FastAPI client testing
- Run with `uv run pytest -v` for verbose output

## Extensibility & Future-Proofing

### Adding New Modules

When creating new feature modules:
1. Follow the `partN/` or `partN/project-name/` structure
2. Include these files as needed:
   - `api_*.py` - FastAPI routes and lifespan
   - `schemas.py` - Request/response models
   - `models.py` - ML model code (if applicable)
   - `dependencies.py` - FastAPI dependencies
   - `*_utils.py` - Module-specific utilities
3. Update this file (`CLAUDE.md` or `AGENTS.md`) if introducing new conventions

### Adapting to New Tech

If the stack evolves (e.g., new package manager, framework):
1. Update **Tech Stack** section with new tooling
2. Update **Essential Commands** with new command patterns
3. Update **What NOT to Do** with deprecated practices
4. Keep **Key Patterns** focused on current conventions

### Multi-Project Usage

To adapt this template for other projects:
1. Update **Project Identity** (name, purpose, package name)
2. Replace **Architecture** with your module structure
3. Keep **Key Patterns** relevant to your stack
4. Update **Tech Stack** and **Code Style** to match your tools
5. Customize **Agent-Specific Guidance** for your workflows

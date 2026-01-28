# Project Guide

## 1. Project Setup

**Name**: `genai-services-fastapi`
**Package**: `genai_services` (import path)
**Root**: Directory containing `pyproject.toml` and `settings.py`

### Tech Stack
- **Python**: 3.11 (strict: `>=3.11,<3.12`)
- **Package Manager**: `uv` (not pip/poetry)
- **Web**: FastAPI + Pydantic
- **ML**: PyTorch, Transformers, Diffusers, Accelerate
- **Vector DB**: Qdrant (RAG/semantic search)
- **PDF**: pypdf for text extraction
- **Embeddings**: jina-embeddings-v2-base-en (768d)
- **Integrations**: OpenAI, LangChain, BentoML
- **Quality**: ruff, mypy/pyrefly, bandit, pre-commit

### Architecture
```
src/genai_services/
├── part*/                         # Feature modules
│   ├── api_*.py                  # FastAPI apps
│   ├── models.py                 # ML model loading
│   ├── schemas.py                # Pydantic models
│   ├── dependencies.py           # FastAPI dependencies
│   ├── client_*.py               # Client code
│   └── project_*/                # Sub-projects
│       ├── api_*.py
│       ├── *.py                  # Domain logic
│       └── uploads/              # Runtime data (gitignored)
├── utils.py                       # Shared utilities
└── __init__.py
settings.py (root)                 # Pydantic settings
```

### Environment Setup
Required in `.env`:
- `OPENAI_API_KEY` (pattern: `sk-proj-...`)
- Optional: `DATABASE_URL`, `CORS_WHITELIST`, `app_secret`

**After cloning or restarting IDE:**
```bash
uv sync  # Installs dependencies + package in editable mode (package = true in pyproject.toml)
```

## 2. Development Patterns

### FastAPI
- **Model Loading**: Lifespan context managers
- **Model Storage**: Module-level `models = {}` dict or `app.state`
- **Response Types**: `StreamingResponse` for audio/images, Pydantic for JSON
- **Background Tasks**: Use `BackgroundTasks` for PDF extraction, vector storage. Errors are silent - add explicit `loguru.logger` logging.

### Pydantic
- **Type Annotations**: `Annotated[type, Field(...)]`
- **Validation**: `AfterValidator` for complex logic
- **Computed Fields**: `@computed_field` for derived properties
- **Settings**: `pydantic-settings` with `.env` (search `BaseSettings`)

### Async
- **File I/O**: Always use `aiofiles`
- **HTTP**: `httpx.AsyncClient` or `aiohttp.ClientSession` with context managers
- **Concurrent**: `asyncio.gather()` for parallel ops

### ML Models
- **Device**: `accelerator.device` (MPS for Apple Silicon, else CPU)
- **Pipelines**: HuggingFace for text generation
- **Manual**: `AutoModel` + `AutoProcessor` for audio/custom

### RAG/Vector DB
- **Client**: `AsyncQdrantClient` for async operations
- **Collections**: Check exists before creating; use `recreate_collection` with `return`
- **Embeddings**: jina-embeddings-v2-base-en (768d) via `AutoModel.from_pretrained`
- **Chunking**: 512 characters default
- **Search**: Cosine distance, 0.7 score threshold
- **Pipeline**: Extract → Clean → Chunk → Embed → Store → Retrieve → Generate
- **Background**: PDF extraction + vector storage in `BackgroundTasks` - errors may be silent

### Code Style
- **Line Length**: ruff config
- **Quotes**: Single quotes
- **Imports**: Sorted with ruff, first-party = `genai_services`
- **Type Hints**: Required everywhere (pyrefly strict)
- **Docstrings**: Simple one-liners
- **Logging**: `loguru` logger (`from loguru import logger`)

## 3. Commands & Discovery

### Essential Commands
```bash
# Dependencies
uv sync                                  # Install all
uv pip install -e . --force-reinstall    # Install project in editable mode
uv add <package>                         # Add package

# Testing & Quality
uv run pytest                            # All tests
uv run pytest tests/test_*.py -v        # Specific pattern
uv run pre-commit run --all-files       # All linters
uv run ruff check .                     # Lint
uv run ruff format .                    # Format
uv run pyrefly check .                 # Type check

# Running Services
uv run fastapi dev <path/to/api_*.py>   # FastAPI dev server
uv run bentoml serve <path/to/bento.py>:<ServiceClass>
uv run streamlit run <path/to/streamlit_app.py>

# Running Scripts (as module, not file path)
uv run python -m genai_services.part2.project_2_rag.service

# Vector DB (Qdrant)
curl http://localhost:6333/collections/<collection_name>
curl http://localhost:6333/collections
```

### File Discovery
```bash
# Find components
grep -r "FastAPI(" src/ --include="*.py"
grep -r "streamlit" src/ --include="*.py"
grep -r "BaseModel" src/ --include="schemas.py"
find . -name "settings.py" -o -name "*config*.py"
grep -r "def load_.*_model" src/ --include="*.py"
grep -r "@app\.(get|post|put|delete)" src/ --include="*.py"
grep -r "aiofiles" src/ --include="*.py"
```

### File Discovery Patterns
- **API**: `api_*.py` or `FastAPI()` instantiation
- **Schemas**: `schemas.py` or `BaseModel` subclasses
- **ML Models**: `models.py` or `load_*_model()` functions
- **Settings**: `settings.py` or `BaseSettings` subclasses
- **Utils**: `utils.py` for shared helpers
- **Tests**: `tests/test_*.py`

### Code Reading Order
1. `api_*.py` → endpoints, request flow
2. `schemas.py` → data models, validation
3. `models.py` → ML model loading
4. `dependencies.py` → FastAPI dependencies
5. `*.py` → business logic

### Common Patterns to Search
- **File Upload**: `UploadFile` or `aiofiles`
- **Web Scraping**: `aiohttp.ClientSession` or `BeautifulSoup`
- **Text Generation**: `generate_text()` or HuggingFace `pipeline()`
- **Buffers**: `BytesIO` conversions
- **Async Context**: `@asynccontextmanager`

## 4. Development Rules

### ✅ What to Do
- Use `uv sync` + `uv pip install -e . --force-reinstall` after IDE restart
- Use `uv add <package>` for dependencies
- Use `uv run <command>` for commands
- Run scripts as modules: `uv run python -m genai_services.module`
- Use `loguru.logger` for logging
- Use `aiofiles` for async file I/O

### ❌ What NOT to Do
- Don't use `pip install` (use `uv add` or `uv sync`)
- Don't use `uv run pip install -e .` (use `uv pip install -e .`)
- Don't run scripts as file paths: `uv run python src/.../script.py`
- Don't run Python without `uv run` prefix
- Don't scatter utilities (consolidate in `utils.py`)
- Don't add dependencies without version constraints
- Don't use `print()` for logging
- Don't use `open()` for async code
- Don't convert `PageObject` to string (use `.extract_text()` for pypdf)
- Don't assume background tasks succeed (add logging)
- Don't use `query_vector=` with Qdrant's `query_points()` (use `query=`)

### Adding New Features

**API Endpoints**
- Add to `api_*.py` (find via: `find src -name "api_*.py"`)
- Use lifespan for models, Pydantic schemas, type hints

**Pydantic Models**
- Add to `schemas.py` or create if absent
- Use `Annotated[type, Field(...)]` pattern

**ML Models**
- Add loading logic to `models.py`
- Add to lifespan context manager
- Store in `models` dict

**Dependencies**
- Use `uv add <package>` (updates `pyproject.toml`)

**Environment Variables**
- Add to settings file (search `BaseSettings`)
- Document in `.env.example`

## 5. Debugging

### Systematic Approach

**1. API Layer**
- Read stack traces bottom-to-top
- Identify exact failing line/operation
- Check API docs for correct parameters
- Use Context7 MCP to verify API contracts

**2. Data Pipeline**
- Verify data at each stage (don't assume prior stages worked)
- RAG: PDF → text → embeddings → vector DB → retrieval
- Inspect intermediate outputs (files, DB state, API responses)
- Use CLI tools to verify external service state

**3. Type & Contract Validation**
- Check function signatures match API docs
- Verify data types match downstream expectations
- Don't trust variable names - verify actual parameter names

**4. External Service State**
- Check DBs/APIs contain expected data
- Qdrant: Verify collection exists, point count > 0
- Files: Verify actual content, not metadata
- Don't assume background tasks completed

**5. Logging**
- Add logging at pipeline boundaries
- Log inputs/outputs (sizes, counts, errors)
- Background tasks: Explicit success/failure logging
- Use `loguru.logger.debug()` for troubleshooting

**6. Isolated Testing**
- Test components independently
- Create minimal reproduction scripts
- Verify retrieval before generation
- Test embedding separately from storage

### Commands
```bash
# External service state
curl http://localhost:6333/collections/<name>
docker ps
docker logs <container_id>

# Data quality
head -30 <file.txt>
cat <file.txt> | wc -l

# Interactive testing
uv run python
# >>> from genai_services.module import func
# >>> result = func(test_input)

# Logs
tail -f <log_file>
```

### Checklist
1. ✅ Read full stack trace - identify failing operation
2. ✅ Verify API parameters against docs
3. ✅ Check external service state (DB, files)
4. ✅ Verify data at each pipeline stage
5. ✅ Add logging before investigating
6. ✅ Test component in isolation
7. ✅ Check background tasks completed (logs, DB)
8. ✅ Validate types/shapes match contracts

## 6. RAG-Specific Guidance

### Common Pitfalls
- **PDF Extraction**: Must call `page.extract_text()`, not convert `PageObject` to string
- **Qdrant API**: Use `query=` parameter, not `query_vector=` in `query_points()`
- **Collection Logic**: Add `return` after `recreate_collection` to prevent duplicate creation
- **Background Tasks**: Errors are silent - check logs and vector DB state directly
- **Empty Results**: Verify pipeline end-to-end: PDF → text → vector DB points → retrieval

### Verification Steps
1. Check collection: `curl http://localhost:6333/collections/<name>`
2. Verify point count > 0 before testing retrieval
3. Check `.txt` files contain text, not PDF metadata
4. Test retrieval independently before generation
5. Validate similarity scores (typically > 0.7)

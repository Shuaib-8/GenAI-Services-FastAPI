from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Body, Depends, FastAPI, Request

from genai_services.part1.models import generate_text, load_text_model
from genai_services.part1.schemas import TextModelRequest, TextModelResponse
from genai_services.utils import normalize_text

# Use relative imports (works when running as package with fastapi run)
from .dependencies import get_urls_content
from .scraper import WebScraper

_body_default = Body(..., description="Text model request")

models = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    models["text"] = load_text_model()
    scraper = WebScraper()
    await scraper.__aenter__()
    app.state.scraper = scraper

    yield

    await scraper.__aexit__(None, None, None)
    app.state.scraper = None

    models.clear()


app = FastAPI(lifespan=lifespan)


@app.post("/generate/scrape/text", response_model_exclude_defaults=True)
async def scrape_text(
    request: Request,
    body: TextModelRequest = _body_default,
    urls_content: str = Depends(get_urls_content),
) -> TextModelResponse:
    pipe = models["text"]
    prompt: str = body.prompt + " " + urls_content
    output: str = generate_text(pipe, prompt, body.temperature)
    return TextModelResponse(
        ip=request.client.host if request.client else None,
        content=normalize_text(output),
        model=body.model,
        temperature=body.temperature,
    )

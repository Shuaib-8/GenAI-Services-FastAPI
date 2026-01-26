from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import (
    BackgroundTasks,
    Body,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from loguru import logger
from transformers import Pipeline

from genai_services.part1.models import generate_text, load_text_model
from genai_services.part1.schemas import TextModelRequest, TextModelResponse
from genai_services.utils import normalize_text

from .dependencies import get_rag_content
from .extractor import pdf_text_extractor
from .upload import save_file
from .vector_service import VectorDBService

_body_default = Body(..., description="Text model request")

models: dict[str, Pipeline] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    models["text"] = load_text_model()

    yield

    models.clear()


app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def file_upload_controller(
    file: Annotated[UploadFile, File(description="Uploaded PDF documents.")],
    bg_text_processor: BackgroundTasks,
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        ) from Exception("File must be a PDF")
    try:
        filepath: str = str(await save_file(file))
        bg_text_processor.add_task(pdf_text_extractor, filepath)
        logger.info(f"File {filepath} uploaded successfully")
        vector_service = VectorDBService()
        bg_text_processor.add_task(
            vector_service.store_file_content_in_db,
            filepath.replace("pdf", "txt"),
            chunk_size=512,
            collection_name="knowledgebase",
            collection_size=768,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving the file - Error: {exc}",
        ) from exc
    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
    }


@app.post("/generate/text", response_model_exclude_defaults=True)
async def generate_text_controller(
    request: Request,
    body: TextModelRequest = _body_default,
    rag_content: str = Depends(get_rag_content),
) -> TextModelResponse:
    logger.info("Generating text...")
    try:
        pipe: Pipeline = models["text"]
        prompt: str = body.prompt + " " + rag_content
        output: str = generate_text(pipe, prompt, body.temperature)
        return TextModelResponse(
            content=normalize_text(output),
            ip=request.client.host if request.client else None,
            model=body.model,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating text - Error: {exc}",
        ) from exc
    finally:
        logger.success("Text generation completed successfully")

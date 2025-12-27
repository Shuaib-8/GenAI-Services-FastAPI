from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Response, status
from fastapi.responses import PlainTextResponse, StreamingResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI

from models import (
    generate_audio,
    generate_text,
    load_audio_model,
    load_text_model,
)
from schemas import VoicePresets
from utils import audio_array_to_buffer

models = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    models["text"] = load_text_model()
    models["audio"] = load_audio_model()

    yield

    models.clear()


app = FastAPI(lifespan=lifespan)
openai_client = OpenAI()


@app.get("/generate/text", response_class=PlainTextResponse)
def serve_language_model_controller(prompt: str) -> PlainTextResponse:
    pipe = models["text"]
    output = generate_text(pipe, prompt)
    return PlainTextResponse(content=output)


@app.get(
    "/generate/audio",
    responses={status.HTTP_200_OK: {"content": {"audio/wav": {}}}},
    response_class=StreamingResponse,
)
def serve_text_to_audio_model_controller(
    prompt: str, preset: VoicePresets = "v2/en_speaker_1"
) -> StreamingResponse:
    processor, model = models["audio"]
    output, sample_rate = generate_audio(processor, model, prompt, preset)
    buffer = audio_array_to_buffer(output, sample_rate)
    return StreamingResponse(buffer, media_type="audio/wav")


@app.get(
    "/generate/bentoml/image",
    responses={status.HTTP_200_OK: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def serve_bentoml_text_to_image_model_controller(prompt: str) -> Response:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://localhost:5001/generate/image", json={"prompt": prompt}
        )
    return Response(content=response.content, media_type="image/png")


@app.get("/generate/openai/text", response_class=Response)
def serve_openai_text_model_controller(prompt: str) -> str | None:
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


@app.get("/generate/langchain/text", response_class=PlainTextResponse)
def serve_langchain_text_model_controller(prompt: str) -> PlainTextResponse:
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("user", "{prompt}"),
        ]
    )
    model = ChatOpenAI(model="gpt-4o-mini")
    output_parser = StrOutputParser()
    chain = prompt_template | model | output_parser
    result = chain.invoke({"prompt": prompt})
    return PlainTextResponse(content=result)

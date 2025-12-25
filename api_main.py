from fastapi import FastAPI, Response, status
from fastapi.responses import PlainTextResponse, StreamingResponse

from models import (
    generate_audio,
    generate_image,
    generate_text,
    load_audio_model,
    load_image_model,
    load_text_model,
)
from schemas import VoicePresets
from utils import audio_array_to_buffer, image_array_to_buffer

app = FastAPI()


@app.get("/generate/text", response_class=PlainTextResponse)
def serve_language_model_controller(prompt: str) -> PlainTextResponse:
    pipe = load_text_model()
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
    processor, model = load_audio_model()
    output, sample_rate = generate_audio(processor, model, prompt, preset)
    buffer = audio_array_to_buffer(output, sample_rate)
    return StreamingResponse(buffer, media_type="audio/wav")


@app.get(
    "/generate/image",
    responses={status.HTTP_200_OK: {"content": {"image/png": {}}}},
    response_class=Response,
)
def serve_text_to_image_model_controller(prompt: str) -> StreamingResponse:
    pipe = load_image_model()
    output = generate_image(pipe, prompt)
    buffer = image_array_to_buffer(output)
    return Response(content=buffer, media_type="image/png")

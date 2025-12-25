from fastapi import FastAPI, status
from fastapi.responses import PlainTextResponse, StreamingResponse

from models import generate_audio, generate_text, load_audio_model, load_text_model
from schemas import VoicePresets
from utils import audio_array_to_buffer

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

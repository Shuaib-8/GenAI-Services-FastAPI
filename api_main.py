from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from models import generate_text, load_text_model

app = FastAPI()


@app.get("/generate/text", response_class=PlainTextResponse)
def serve_language_model_controller(prompt: str) -> PlainTextResponse:
    pipe = load_text_model()
    output = generate_text(pipe, prompt)
    return PlainTextResponse(content=output)

from fastapi import Body, FastAPI, Request

from genai_services.part1.schemas import TextModelRequest, TextModelResponse
from genai_services.part2.ollama_async_model_serving import (
    LOCAL_CONFIG,
    generate_text_completion,
)
from genai_services.utils import normalize_text

app = FastAPI()

_body_default = Body(..., description="Text model request")


@app.post("/generate/text")
async def serve_text_to_text_controller(
    request: Request,
    body: TextModelRequest = _body_default,
) -> TextModelResponse:
    output = await generate_text_completion(
        prompt=body.prompt,
        model=body.model,
        config=LOCAL_CONFIG,
        use_cloud=False,
        temperature=body.temperature,
    )
    return TextModelResponse(
        content=normalize_text(output),
        model=body.model,
        ip=request.client.host if request.client else None,
    )

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel

VoicePresets = Literal["v2/en_speaker_1", "v2/en_speaker_9"]


class ModelRequest(BaseModel):
    prompt: str


class ModelResponse(BaseModel):
    request_id: str
    ip: str | None
    content: str | None
    created_at: datetime = datetime.now()


class TextModelRequest(ModelRequest):
    model: Literal["gpt-4o-mini", "gpt-4o"]
    temperature: float = 0.0


class TextModelResponse(ModelResponse):
    tokens: int


ImageSize = Annotated[tuple[int, int], "Width and height of the image in pixels"]


class ImageModelRequest(ModelRequest):
    model: Literal["dall-e-3", "dall-e-2"]
    output_size: ImageSize
    num_inference_steps: int = 20


class ImageModelResponse(ModelResponse):
    size: ImageSize
    url: str

from datetime import datetime
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, IPvAnyAddress, PositiveInt

VoicePresets = Literal["v2/en_speaker_1", "v2/en_speaker_9"]


class ModelRequest(BaseModel):
    prompt: Annotated[str, Field(min_length=1, max_length=1000)]


class ModelResponse(BaseModel):
    request_id: Annotated[str, Field(default_factory=lambda: uuid4().hex)]
    # No default value for ip to allow for None - raise validation error if None or no valid IP address is provided
    ip: Annotated[str, IPvAnyAddress] | None
    content: Annotated[str | None, Field(min_length=0, max_length=100000)]
    created_at: datetime = datetime.now()


class TextModelRequest(ModelRequest):
    model: Literal["gpt-4o-mini", "gpt-4o"]
    temperature: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]


class TextModelResponse(ModelResponse):
    tokens: Annotated[int, Field(ge=0)]


ImageSize = Annotated[
    tuple[PositiveInt, PositiveInt], "Width and height of the image in pixels"
]


class ImageModelRequest(ModelRequest):
    model: Literal["dall-e-3", "dall-e-2"]
    output_size: ImageSize
    num_inference_steps: Annotated[int, Field(ge=0, le=2000, default=20)]


class ImageModelResponse(ModelResponse):
    size: ImageSize
    url: Annotated[str, HttpUrl] | None = None

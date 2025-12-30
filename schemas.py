from datetime import datetime
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    HttpUrl,
    IPvAnyAddress,
    PositiveInt,
    computed_field,
    validate_call,
)

from utils import count_tokens

VoicePresets = Annotated[
    Literal["v2/en_speaker_1", "v2/en_speaker_9"], "Supported voice presets"
]
ImageSize = Annotated[
    tuple[PositiveInt, PositiveInt], "Width and height of the image in pixels"
]
SupportedImageModels = Annotated[
    Literal["tinysd", "sd1.5"], "Supported image generation models"
]
SupportedTextModels = Annotated[
    Literal["gpt-4o-mini", "gpt-4o"], "Supported text generation models"
]


class ModelRequest(BaseModel):
    prompt: Annotated[str, Field(min_length=1, max_length=1000)]


class ModelResponse(BaseModel):
    request_id: Annotated[str, Field(default_factory=lambda: uuid4().hex)]
    # No default value for ip to allow for None - raise validation error if None or no valid IP address is provided
    ip: Annotated[str, IPvAnyAddress] | None
    content: Annotated[str | None, Field(min_length=0, max_length=100000)]
    created_at: datetime = datetime.now()


class TextModelRequest(ModelRequest):
    model: SupportedTextModels
    temperature: Annotated[
        float,
        Field(
            ge=0.0,
            le=1.0,
            default=0.01,
            description="Controls randomness in text generation. 0.0 is deterministic, 1.0 is most random.",
        ),
    ]


class TextModelResponse(ModelResponse):
    model: SupportedTextModels
    rate: Annotated[
        float,
        Field(ge=0.0, default=0.01, exclude=True, description="Price rate per token"),
    ]
    temperature: Annotated[
        float,
        Field(
            ge=0.0, le=1.0, default=0.01, description="Temperature used for generation"
        ),
    ]

    @computed_field
    def tokens(self) -> int:
        return count_tokens(self.content)

    @computed_field
    def price(self) -> float:
        return self.tokens * self.rate


ImageSize = Annotated[
    tuple[PositiveInt, PositiveInt], "Width and height of the image in pixels"
]
SupportedImageModels = Annotated[
    Literal["tinysd", "sd1.5"], "Supported image generation models"
]
SupportedTextModels = Annotated[
    Literal["gpt-4o-mini", "gpt-4o"], "Supported text generation models"
]


@validate_call
def is_square_image(value: ImageSize) -> ImageSize:
    if value[0] / value[1] != 1:
        raise ValueError("Image must be square")
    if value[0] not in [512, 1024]:
        raise ValueError(f"Image width {value[0]} must be 512 or 1024")
    if value[1] not in [512, 1024]:
        raise ValueError(f"Image height {value[1]} must be 512 or 1024")
    return value


@validate_call
def is_valid_inference_steps(
    num_inference_steps: int, model: SupportedImageModels
) -> int:
    if model == "tinysd" and num_inference_steps > 2000:
        raise ValueError("TinySD model only supports up to 2000 inference steps")
    elif model == "sd1.5" and num_inference_steps > 50:
        raise ValueError("SD1.5 model only supports up to 50 inference steps")
    return num_inference_steps


OutputSize = Annotated[ImageSize, AfterValidator(is_square_image)]
InferenceSteps = Annotated[
    int, AfterValidator(lambda v, values: is_valid_inference_steps(v, values["model"]))
]


class ImageModelRequest(ModelRequest):
    model: SupportedImageModels
    output_size: OutputSize
    num_inference_steps: InferenceSteps = 20


class ImageModelResponse(ModelResponse):
    size: ImageSize
    url: Annotated[str, HttpUrl] | None = None

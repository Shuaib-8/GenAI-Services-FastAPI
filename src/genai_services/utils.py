import re
from io import BytesIO
from typing import Literal

import numpy as np
import soundfile
from PIL import Image


def audio_array_to_buffer(audio_array: np.array, sample_rate: int) -> BytesIO:
    """Convert an audio array to a buffer."""
    buffer = BytesIO()
    # Specify format explicitly for BytesIO objects
    soundfile.write(buffer, audio_array, sample_rate, format="wav")
    buffer.seek(0)
    return buffer


def image_array_to_buffer(
    image_array: Image.Image, img_format: Literal["PNG", "JPEG"] = "PNG"
) -> bytes:
    """Convert an image array to a buffer."""
    buffer = BytesIO()
    image_array.save(buffer, format=img_format)
    buffer.seek(0)
    return buffer.getvalue()


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text."""
    return len(text.split())


def normalize_text(text: str | None) -> str | None:
    """Normalize text: handle encodings, remove escape sequences and control chars."""
    if text is None:
        return None
    # Handle bytes with fallback encoding
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    # Normalize all whitespace (including \n, \t, \r, etc.) to single space
    text = re.sub(r"\s+", " ", text)
    # Remove control characters
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    return text.strip()

from io import BytesIO

import numpy as np
import soundfile


def audio_array_to_buffer(audio_array: np.array, sample_rate: int) -> BytesIO:
    """Convert an audio array to a buffer."""
    buffer = BytesIO()
    # Specify format explicitly for BytesIO objects
    soundfile.write(buffer, audio_array, sample_rate, format="wav")
    buffer.seek(0)
    return buffer


def buffer_to_audio_array(buffer: BytesIO) -> np.array:
    """Convert a buffer to an audio array."""
    audio_array, sample_rate = soundfile.read(buffer)
    return audio_array, sample_rate

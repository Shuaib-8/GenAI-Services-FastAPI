import re
from collections.abc import AsyncGenerator
from typing import Any

import aiofiles
from transformers import AutoModel

DEFAULT_CHUNK_SIZE: int = 1024 * 1024 * 50  # 50MB

embedder = AutoModel.from_pretrained(
    "jinaai/jina-embeddings-v2-base-en",
    trust_remote_code=True,
)


async def load(filepath: str) -> AsyncGenerator[str, Any]:
    """Load a file and return its content as a string."""
    async with aiofiles.open(filepath, encoding="utf-8") as f:
        while chunk := await f.read(DEFAULT_CHUNK_SIZE):
            yield chunk


def clean(text: str) -> str:
    """Clean the text of the file."""
    t = text.replace("\n", " ")  # replace newlines with a space
    t = re.sub(r"\s+", " ", t)  # replace multiple spaces with a single space
    t = re.sub(r"\. ,", "", t)  # remove periods and commas
    t = t.replace("..", ".")  # remove double periods
    t = t.replace(". .", ".")  # remove double periods
    cleaned_text = t.replace("\n", " ").strip()  # remove newlines and strip whitespace
    return cleaned_text


def embed(text: str) -> list[float]:
    """Embed the text using the embedder."""
    return embedder.encode(text).tolist()

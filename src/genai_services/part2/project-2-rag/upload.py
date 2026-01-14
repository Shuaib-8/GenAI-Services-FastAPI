from pathlib import Path

import aiofiles
from aiofiles.os import makedirs
from fastapi import UploadFile

DEFAULT_CHUNK_SIZE = 1000 * 1024 * 50  # 50MB

UPLOAD_DIR = Path(__file__).parent / "uploads"


async def save_file(file: UploadFile) -> Path:
    """Save an uploaded file to a specified path asynchronously."""
    await makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = (
        UPLOAD_DIR / file.filename if file.filename else UPLOAD_DIR / "unnamed.txt"
    )
    async with aiofiles.open(filepath, "wb") as f:
        while chunk := await file.read(DEFAULT_CHUNK_SIZE):
            await f.write(chunk)

    return filepath

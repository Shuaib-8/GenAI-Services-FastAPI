from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from .upload import save_file

app = FastAPI()


@app.post("/upload")
async def file_upload_controller(
    file: Annotated[UploadFile, File(description="Uploaded PDF documents.")],
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        ) from Exception("File must be a PDF")
    try:
        await save_file(file)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving the file - Error: {exc}",
        ) from exc
    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
    }

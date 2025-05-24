from typing import Annotated

import magic  # brew install libmagic
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from starlette import status
from pathlib import Path

load_dotenv()

SUPPORTED_FILES = {"application/pdf": "pdf", "image/png": "png"}

app = FastAPI(
    title="RAG OnDemand",
    description="An app enabling ondemand RAG queries on documents.",
)


@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"message": "The app is up!"}


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploaddoc/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()
    file_size = len(contents)
    file_type = magic.from_buffer(buffer=contents, mime=True)
    if not file_type in SUPPORTED_FILES:
        return {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "body": f"Unsupported file type: {file_type}.",
        }

    return {
        "filename": Path(file.filename).name,
        "file_size": file_size,
        "file_type": file_type,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)

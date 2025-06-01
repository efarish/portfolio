from pathlib import Path
from typing import Annotated
from uuid import uuid4

import magic  # brew install libmagic
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from starlette import status
from storage import Storage

load_dotenv()

import llama_index_util as liu

SUPPORTED_FILES = {"application/pdf": "pdf", "image/png": "png"}


class SessionRequest(BaseModel):
    session_id: str


class PrepareRequest(SessionRequest):
    recreate: bool


class QueryRequest(SessionRequest):
    query: str


app = FastAPI(
    title="RAG OnDemand",
    description="An app enabling ondemand RAG queries on documents.",
)


def _return(statusCode, **kwargs):
    return {"statusCode": statusCode, **kwargs}


@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return _return(status.HTTP_200_OK, body="The app is up!")


@app.get(
    "/create_session", status_code=status.HTTP_200_OK, response_model=SessionRequest
)
async def create_session():
    return _return(status.HTTP_200_OK, session_id=str(uuid4()))


@app.post("/upload")
async def create_upload_file(
    session_id: Annotated[str, Form()], file: UploadFile = File(...)
):
    contents = await file.read()
    file_size = len(contents)
    file_type = magic.from_buffer(buffer=contents, mime=True)
    if not file_type in SUPPORTED_FILES:
        return _return(
            status.HTTP_400_BAD_REQUEST, body=f"Unsupported file type: {file_type}."
        )
    try:
        Storage("S3").save(session_id, Path(file.filename).name, contents)
    except ValueError as e:
        return _return(status.HTTP_500_INTERNAL_SERVER_ERROR, body=str(e))

    return _return(
        status.HTTP_201_CREATED,
        body=f"File {Path(file.filename).name} uploaded.",
    )


@app.post("/prepare")
async def prepare(prepare_request: PrepareRequest):
    await liu.create_index(
        prepare_request.session_id, recreate=prepare_request.recreate
    )
    return _return(status.HTTP_200_OK)


@app.post("/query")
async def query(query_request: QueryRequest):
    response = await liu.query(query_request.session_id, query_request.query)
    return _return(status.HTTP_200_OK, body=response)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)

import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.environ.get("S3_BUCKET")
AWS_KEY = os.environ.get("AWS_KEY")
AWS_SECRET = os.environ.get("AWS_SECRET")

class Storage:

    def __new__(cls, storage_type: str):
        match storage_type:
            case "S3":
                return S3Storage
            case "FileSystem":
                return FSStorage
            case _:
                raise ValueError(f"Invalid storage type {storage_type}")

    @staticmethod
    def save(session_id: str, file_name: str, contents: bytes) -> None:
        raise NotImplementedError()


class S3Storage(Storage):

    @staticmethod
    def save(session_id: str, file_name: str, contents: bytes) -> None:

        s3 = boto3.client("s3", aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
        key = f"{session_id}/files/{file_name}"
        s3_upload = s3.put_object(Bucket=S3_BUCKET, Key=key, Body=contents)

        if not s3_upload["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"S3 error: {s3_upload}")
            raise ValueError("Failed to store file.")


class FSStorage(Storage):

    @staticmethod
    def save(session_id: str, file_name: str, contents: bytes) -> None:

        file_path = f"./storage/{session_id}"
        path = Path(file_path)
        path.mkdir(parents=True, exist_ok=True)
        file = path / file_name
        file.write_bytes(contents)

import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.environ.get("S3_BUCKET")


def save(session_id: str, file_name: str, contents: bytes) -> str:

    s3 = boto3.client("s3")
    key = f"{session_id}/{file_name}"
    s3_upload = s3.put_object(Bucket=S3_BUCKET, Key=key, Body=contents)

    if not s3_upload["ResponseMetadata"]["HTTPStatusCode"] == 200:
        print(f"S3 error: {s3_upload}")
        raise ValueError("Failed to store file.")

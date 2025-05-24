import boto3
import os


S3_BUCKET = os.environ.get("S3_BUCKET")


s3 = boto3.client("s3")
s3_upload = s3.put_object(Bucket=S3_BUCKET, Key=key, Body=decode_body)

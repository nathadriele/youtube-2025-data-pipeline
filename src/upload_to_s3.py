import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# AWS credentials and config
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FILE_KEY = os.getenv("S3_FILE_KEY", "youtube_2025_dataset.csv")
LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH", "youtube_2025_dataset.csv")

def upload_file_to_s3():
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    s3.upload_file(LOCAL_FILE_PATH, S3_BUCKET_NAME, S3_FILE_KEY)
    print(f"File '{LOCAL_FILE_PATH}' uploaded to S3 bucket '{S3_BUCKET_NAME}' as '{S3_FILE_KEY}'")

if

import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def load_config() -> dict:
    """
    Load and validate required environment variables.
    """
    load_dotenv()

    config = {
        "aws_access_key": os.getenv("AWS_ACCESS_KEY"),
        "aws_secret_key": os.getenv("AWS_SECRET_KEY"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
        "s3_file_key": os.getenv("S3_FILE_KEY", "youtube_2025_dataset.csv"),
        "local_file_path": os.getenv("LOCAL_FILE_PATH", "youtube_2025_dataset.csv"),
    }

    missing_vars = [
        key for key in ["aws_access_key", "aws_secret_key", "s3_bucket_name"]
        if not config.get(key)
    ]

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return config


def validate_local_file(file_path: str) -> None:
    """
    Validate whether the local file exists before upload.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Local file not found: {file_path}")


def get_s3_client(config: dict):
    """
    Create and return an S3 client.
    """
    return boto3.client(
        "s3",
        aws_access_key_id=config["aws_access_key"],
        aws_secret_access_key=config["aws_secret_key"],
    )


def upload_file_to_s3(s3_client, local_file_path: str, bucket_name: str, s3_file_key: str) -> None:
    """
    Upload a local file to S3.
    """
    logging.info("Starting file upload to S3...")
    s3_client.upload_file(local_file_path, bucket_name, s3_file_key)
    logging.info(
        "File successfully uploaded to S3 | local_file=%s | bucket=%s | key=%s",
        local_file_path,
        bucket_name,
        s3_file_key,
    )


def main() -> None:
    """
    Main execution flow.
    """
    try:
        config = load_config()
        validate_local_file(config["local_file_path"])
        s3_client = get_s3_client(config)

        upload_file_to_s3(
            s3_client=s3_client,
            local_file_path=config["local_file_path"],
            bucket_name=config["s3_bucket_name"],
            s3_file_key=config["s3_file_key"],
        )

        logging.info("Upload pipeline completed successfully.")

    except (FileNotFoundError, ValueError) as exc:
        logging.error("Validation error: %s", exc)
        raise

    except (BotoCoreError, ClientError) as exc:
        logging.error("AWS S3 error: %s", exc)
        raise

    except Exception as exc:
        logging.error("Unexpected error during upload: %s", exc)
        raise


if __name__ == "__main__":
    main()
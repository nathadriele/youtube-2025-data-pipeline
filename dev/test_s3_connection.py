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
    Load and validate required environment variables for S3 connection.
    """
    load_dotenv()

    config = {
        "aws_access_key": os.getenv("AWS_ACCESS_KEY"),
        "aws_secret_key": os.getenv("AWS_SECRET_KEY"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
        "aws_region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
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


def get_s3_client(config: dict):
    """
    Create and return an S3 client.
    """
    return boto3.client(
        "s3",
        aws_access_key_id=config["aws_access_key"],
        aws_secret_access_key=config["aws_secret_key"],
        region_name=config["aws_region"],
    )


def test_s3_connection(s3_client, bucket_name: str) -> None:
    """
    Test the S3 connection by checking bucket accessibility.
    """
    logging.info("Testing S3 connection...")
    s3_client.head_bucket(Bucket=bucket_name)
    logging.info("S3 connection successful. Bucket '%s' is accessible.", bucket_name)


def main() -> None:
    """
    Main execution flow.
    """
    try:
        config = load_config()
        s3_client = get_s3_client(config)
        test_s3_connection(s3_client, config["s3_bucket_name"])
        logging.info("S3 connection test completed successfully.")

    except ValueError as exc:
        logging.error("Configuration error: %s", exc)
        raise

    except (BotoCoreError, ClientError) as exc:
        logging.error("AWS S3 connection error: %s", exc)
        raise

    except Exception as exc:
        logging.error("Unexpected error during S3 connection test: %s", exc)
        raise


if __name__ == "__main__":
    main()
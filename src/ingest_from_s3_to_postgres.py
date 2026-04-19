import logging
import os
from io import StringIO

import boto3
import pandas as pd
import psycopg2
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
        "s3_file_key": os.getenv("S3_FILE_KEY"),
        "db_name": os.getenv("DB_NAME"),
        "db_user": os.getenv("DB_USER"),
        "db_password": os.getenv("DB_PASSWORD"),
        "db_host": os.getenv("DB_HOST"),
        "db_port": os.getenv("DB_PORT", "5432"),
    }

    missing_vars = [key for key, value in config.items() if not value]

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
    )


def extract_csv_from_s3(s3_client, bucket_name: str, file_key: str) -> pd.DataFrame:
    """
    Read CSV file from S3 and return it as a DataFrame.
    """
    logging.info("Reading CSV file from S3...")
    csv_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    csv_data = csv_obj["Body"].read().decode("utf-8")
    df = pd.read_csv(StringIO(csv_data))
    logging.info("CSV successfully loaded from S3.")
    return df


def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names, select required columns, clean and type data.

    Column mapping (CSV original → pipeline):
        Channel Name               → channel_name
        Youtuber Name              → youtuber
        Total Subscribers          → subscribers
        Total Videos               → total_videos
        Engagement Score           → engagement_score
        Content Value Index        → content_value_index
        Metaverse Integration Level → metaverse_integration_level
        Neural Interface Compatible → neural_interface_compatible
    """
    logging.info("Transforming DataFrame...")

    df = df.copy()

    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    column_mapping = {
        "channel_name": "channel_name",
        "youtuber_name": "youtuber",
        "total_subscribers": "subscribers",
        "total_videos": "total_videos",
        "engagement_score": "engagement_score",
        "content_value_index": "content_value_index",
        "metaverse_integration_level": "metaverse_integration_level",
        "neural_interface_compatible": "neural_interface_compatible",
    }

    missing_source = [src for src in column_mapping if src not in df.columns]
    if missing_source:
        raise ValueError(
            f"Missing expected columns in CSV: {', '.join(missing_source)}"
        )

    df = df.rename(columns=column_mapping)
    selected_columns = list(column_mapping.values())
    df = df[selected_columns]

    df["channel_name"] = df["channel_name"].astype(str).str.strip()
    df["youtuber"] = df["youtuber"].astype(str).str.strip()
    df["metaverse_integration_level"] = df["metaverse_integration_level"].astype(str).str.strip()
    df["neural_interface_compatible"] = df["neural_interface_compatible"].astype(str).str.strip()

    numeric_columns = ["subscribers", "total_videos", "engagement_score", "content_value_index"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    df = df.drop_duplicates()

    logging.info("DataFrame transformation completed successfully.")
    return df


def get_postgres_connection(config: dict):
    """
    Create and return a PostgreSQL connection.
    """
    logging.info("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        dbname=config["db_name"],
        user=config["db_user"],
        password=config["db_password"],
        host=config["db_host"],
        port=config["db_port"],
    )
    logging.info("PostgreSQL connection established successfully.")
    return conn


def create_table(cursor) -> None:
    """
    Create target table if it does not exist.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS youtube_2025_dataset (
        channel_name TEXT,
        youtuber TEXT,
        subscribers BIGINT,
        total_videos BIGINT,
        engagement_score BIGINT,
        content_value_index BIGINT,
        metaverse_integration_level TEXT,
        neural_interface_compatible TEXT
    );
    """
    cursor.execute(create_table_query)


def truncate_table(cursor) -> None:
    """
    Clear table before loading data to avoid duplication.
    """
    cursor.execute("TRUNCATE TABLE youtube_2025_dataset;")


def load_dataframe_to_postgres(df: pd.DataFrame, cursor) -> None:
    """
    Load DataFrame into PostgreSQL using COPY.
    """
    logging.info("Loading data into PostgreSQL...")

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    copy_query = """
    COPY youtube_2025_dataset (
        channel_name,
        youtuber,
        subscribers,
        total_videos,
        engagement_score,
        content_value_index,
        metaverse_integration_level,
        neural_interface_compatible
    )
    FROM STDIN WITH (FORMAT CSV)
    """
    cursor.copy_expert(copy_query, buffer)

    logging.info("Data successfully loaded into PostgreSQL.")


def main() -> None:
    """
    Main pipeline execution.
    """
    conn = None
    cursor = None

    try:
        config = load_config()
        s3_client = get_s3_client(config)
        df = extract_csv_from_s3(
            s3_client=s3_client,
            bucket_name=config["s3_bucket_name"],
            file_key=config["s3_file_key"],
        )
        df = transform_dataframe(df)

        conn = get_postgres_connection(config)
        cursor = conn.cursor()

        create_table(cursor)
        truncate_table(cursor)
        load_dataframe_to_postgres(df, cursor)

        conn.commit()
        logging.info("Pipeline completed successfully.")

    except Exception as exc:
        logging.error(f"Pipeline failed: {exc}")
        if conn is not None:
            conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        logging.info("Resources closed.")


if __name__ == "__main__":
    main()
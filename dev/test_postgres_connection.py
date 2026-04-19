import logging
import os

import psycopg2
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def load_config() -> dict:
    """
    Load and validate required environment variables for PostgreSQL connection.
    """
    load_dotenv()

    config = {
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


def test_postgres_connection(config: dict) -> None:
    """
    Test the PostgreSQL connection by executing a simple query.
    """
    logging.info("Testing PostgreSQL connection...")
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            dbname=config["db_name"],
            user=config["db_user"],
            password=config["db_password"],
            host=config["db_host"],
            port=config["db_port"],
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logging.info("PostgreSQL connection successful. Server version: %s", version[0])

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def main() -> None:
    """
    Main execution flow.
    """
    try:
        config = load_config()
        test_postgres_connection(config)
        logging.info("PostgreSQL connection test completed successfully.")

    except ValueError as exc:
        logging.error("Configuration error: %s", exc)
        raise

    except psycopg2.OperationalError as exc:
        logging.error("PostgreSQL connection error: %s", exc)
        raise

    except Exception as exc:
        logging.error("Unexpected error during PostgreSQL connection test: %s", exc)
        raise


if __name__ == "__main__":
    main()

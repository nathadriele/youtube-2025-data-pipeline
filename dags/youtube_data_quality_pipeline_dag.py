from datetime import timedelta
import os

import pendulum
import psycopg2
from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python import PythonOperator


default_args = {
    "owner": "nathadriele",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
}


def get_db_connection():
    """
    Create and return a PostgreSQL connection using environment variables.
    """
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")

    missing_vars = []
    env_vars = {
        "DB_NAME": db_name,
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "DB_HOST": db_host,
        "DB_PORT": db_port,
    }

    for key, value in env_vars.items():
        if not value:
            missing_vars.append(key)

    if missing_vars:
        raise AirflowException(
            f"Missing required database environment variables: {', '.join(missing_vars)}"
        )

    return psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
    )


def check_raw_table_has_rows():
    """
    Validate that the raw table exists and contains data.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM youtube_2025_dataset;")
            row_count = cursor.fetchone()[0]

            if row_count <= 0:
                raise AirflowException(
                    "Data quality check failed: table 'youtube_2025_dataset' is empty."
                )

            print(f"Raw table check passed. Row count: {row_count}")

    except psycopg2.Error as exc:
        raise AirflowException(
            f"Failed to validate raw table 'youtube_2025_dataset': {exc}"
        ) from exc

    finally:
        if conn is not None:
            conn.close()


def check_raw_required_columns_not_null():
    """
    Validate that required columns in the raw table are not fully null.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_rows,
                    COUNT(youtuber) AS youtuber_not_null,
                    COUNT(subscribers) AS subscribers_not_null,
                    COUNT(engagement_score) AS engagement_score_not_null
                FROM youtube_2025_dataset;
                """
            )
            result = cursor.fetchone()

            total_rows = result[0]
            youtuber_not_null = result[1]
            subscribers_not_null = result[2]
            engagement_score_not_null = result[3]

            if total_rows <= 0:
                raise AirflowException(
                    "Data quality check failed: raw table has no rows."
                )

            if youtuber_not_null == 0:
                raise AirflowException(
                    "Data quality check failed: column 'youtuber' is fully null."
                )

            if subscribers_not_null == 0:
                raise AirflowException(
                    "Data quality check failed: column 'subscribers' is fully null."
                )

            if engagement_score_not_null == 0:
                raise AirflowException(
                    "Data quality check failed: column 'engagement_score' is fully null."
                )

            print("Raw required columns null-check passed.")

    except psycopg2.Error as exc:
        raise AirflowException(
            f"Failed to validate required columns in 'youtube_2025_dataset': {exc}"
        ) from exc

    finally:
        if conn is not None:
            conn.close()


def check_mart_table_has_rows():
    """
    Validate that the mart table exists and contains data.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM youtube_summary;")
            row_count = cursor.fetchone()[0]

            if row_count <= 0:
                raise AirflowException(
                    "Data quality check failed: table 'youtube_summary' is empty."
                )

            print(f"Mart table check passed. Row count: {row_count}")

    except psycopg2.Error as exc:
        raise AirflowException(
            f"Failed to validate mart table 'youtube_summary': {exc}"
        ) from exc

    finally:
        if conn is not None:
            conn.close()


with DAG(
    dag_id="youtube_data_quality_pipeline",
    default_args=default_args,
    description="Data quality checks for raw and transformed YouTube tables in PostgreSQL",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["youtube", "data-quality", "postgres", "airflow"],
) as dag:

    check_raw_table_rows = PythonOperator(
        task_id="check_raw_table_rows",
        python_callable=check_raw_table_has_rows,
        execution_timeout=timedelta(minutes=5),
    )

    check_raw_not_null_columns = PythonOperator(
        task_id="check_raw_not_null_columns",
        python_callable=check_raw_required_columns_not_null,
        execution_timeout=timedelta(minutes=5),
    )

    check_mart_table_rows = PythonOperator(
        task_id="check_mart_table_rows",
        python_callable=check_mart_table_has_rows,
        execution_timeout=timedelta(minutes=5),
    )

    check_raw_table_rows >> check_raw_not_null_columns >> check_mart_table_rows
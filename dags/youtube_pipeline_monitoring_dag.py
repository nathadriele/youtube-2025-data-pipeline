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

    env_vars = {
        "DB_NAME": db_name,
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "DB_HOST": db_host,
        "DB_PORT": db_port,
    }

    missing_vars = [key for key, value in env_vars.items() if not value]

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


def check_required_tables_exist():
    """
    Check whether the expected tables exist in the database.
    """
    required_tables = ["youtube_2025_dataset", "youtube_summary"]

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            for table_name in required_tables:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = %s
                    );
                    """,
                    (table_name,),
                )
                exists = cursor.fetchone()[0]

                if not exists:
                    raise AirflowException(
                        f"Monitoring check failed: required table '{table_name}' does not exist."
                    )

            print("Monitoring check passed: all required tables exist.")

    except psycopg2.Error as exc:
        raise AirflowException(
            f"Failed to verify required tables existence: {exc}"
        ) from exc

    finally:
        if conn is not None:
            conn.close()


def monitor_raw_table_volume():
    """
    Monitor whether the raw table has data above a minimum threshold.
    """
    min_raw_rows = int(os.getenv("MIN_RAW_ROWS", "1"))

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM youtube_2025_dataset;")
            row_count = cursor.fetchone()[0]

            if row_count < min_raw_rows:
                raise AirflowException(
                    f"Monitoring check failed: raw table row count ({row_count}) "
                    f"is below the minimum threshold ({min_raw_rows})."
                )

            print(
                f"Monitoring check passed: raw table row count = {row_count}, "
                f"minimum threshold = {min_raw_rows}."
            )

    except psycopg2.Error as exc:
        raise AirflowException(
            f"Failed to monitor raw table volume: {exc}"
        ) from exc

    finally:
        if conn is not None:
            conn.close()


def monitor_mart_table_volume():
    """
    Monitor whether the mart table has data above a minimum threshold.
    """
    min_mart_rows = int(os.getenv("MIN_MART_ROWS", "1"))

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM youtube_summary;")
            row_count = cursor.fetchone()[0]

            if row_count < min_mart_rows:
                raise AirflowException(
                    f"Monitoring check failed: mart table row count ({row_count}) "
                    f"is below the minimum threshold ({min_mart_rows})."
                )

            print(
                f"Monitoring check passed: mart table row count = {row_count}, "
                f"minimum threshold = {min_mart_rows}."
            )

    except psycopg2.Error as exc:
        raise AirflowException(
            f"Failed to monitor mart table volume: {exc}"
        ) from exc

    finally:
        if conn is not None:
            conn.close()


def monitor_negative_values_in_raw_table():
    """
    Monitor whether numeric metrics in the raw table contain invalid negative values.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM youtube_2025_dataset
                WHERE subscribers < 0
                   OR total_videos < 0
                   OR engagement_score < 0
                   OR content_value_index < 0;
                """
            )
            invalid_count = cursor.fetchone()[0]

            if invalid_count > 0:
                raise AirflowException(
                    f"Monitoring check failed: found {invalid_count} rows with negative values "
                    f"in numeric columns."
                )

            print("Monitoring check passed: no negative values found in raw numeric columns.")

    except psycopg2.Error as exc:
        raise AirflowException(
            f"Failed to monitor invalid negative values in raw table: {exc}"
        ) from exc

    finally:
        if conn is not None:
            conn.close()


with DAG(
    dag_id="youtube_pipeline_monitoring",
    default_args=default_args,
    description="Operational monitoring checks for YouTube pipeline tables and metrics",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["youtube", "monitoring", "postgres", "airflow"],
) as dag:

    check_tables = PythonOperator(
        task_id="check_required_tables_exist",
        python_callable=check_required_tables_exist,
        execution_timeout=timedelta(minutes=5),
    )

    monitor_raw_volume = PythonOperator(
        task_id="monitor_raw_table_volume",
        python_callable=monitor_raw_table_volume,
        execution_timeout=timedelta(minutes=5),
    )

    monitor_mart_volume = PythonOperator(
        task_id="monitor_mart_table_volume",
        python_callable=monitor_mart_table_volume,
        execution_timeout=timedelta(minutes=5),
    )

    monitor_negative_values = PythonOperator(
        task_id="monitor_negative_values_in_raw_table",
        python_callable=monitor_negative_values_in_raw_table,
        execution_timeout=timedelta(minutes=5),
    )

    check_tables >> monitor_raw_volume >> monitor_negative_values >> monitor_mart_volume
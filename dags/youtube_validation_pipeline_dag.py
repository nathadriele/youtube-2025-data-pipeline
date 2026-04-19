from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "nathadriele",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
}


with DAG(
    dag_id="youtube_validation_pipeline",
    default_args=default_args,
    description="Validation pipeline for YouTube project infrastructure and connectivity",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["youtube", "validation", "s3", "postgres", "airflow"],
) as dag:

    test_s3_connection = BashOperator(
        task_id="test_s3_connection",
        bash_command="""
        set -e
        python /opt/airflow/dev/test_s3_connection.py
        """,
        execution_timeout=timedelta(minutes=5),
    )

    test_postgres_connection = BashOperator(
        task_id="test_postgres_connection",
        bash_command="""
        set -e
        python /opt/airflow/dev/test_postgres_connection.py
        """,
        execution_timeout=timedelta(minutes=5),
    )

    test_s3_connection >> test_postgres_connection
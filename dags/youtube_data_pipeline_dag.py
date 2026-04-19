from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "nathadriele",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
}


with DAG(
    dag_id="youtube_data_pipeline",
    default_args=default_args,
    description="ETL pipeline for YouTube dataset using AWS S3, Postgres, dbt, and Airflow",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["youtube", "etl", "dbt", "airflow"],
) as dag:

    upload_to_s3 = BashOperator(
        task_id="upload_to_s3",
        bash_command="""
        set -e
        python /opt/airflow/src/upload_to_s3.py
        """,
        execution_timeout=timedelta(minutes=10),
    )

    ingest_from_s3 = BashOperator(
        task_id="ingest_from_s3",
        bash_command="""
        set -e
        python /opt/airflow/src/ingest_from_s3_to_postgres.py
        """,
        execution_timeout=timedelta(minutes=15),
    )

    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="""
        set -e
        dbt run --project-dir /opt/airflow/dbt/youtube --profiles-dir /opt/airflow
        """,
        execution_timeout=timedelta(minutes=15),
    )

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command="""
        set -e
        dbt test --project-dir /opt/airflow/dbt/youtube --profiles-dir /opt/airflow
        """,
        execution_timeout=timedelta(minutes=15),
    )

    upload_to_s3 >> ingest_from_s3 >> run_dbt_models >> run_dbt_tests
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'nathadriele',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'depends_on_past': False,
    'email_on_failure': False,
}

with DAG(
    dag_id='youtube_2025_data_pipeline',
    default_args=default_args,
    description='ETL pipeline for ingesting YouTube dataset from S3 to PostgreSQL and transforming with dbt',
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['youtube', 's3', 'dbt', 'airflow'],
) as dag:

    upload_to_s3 = BashOperator(
        task_id='upload_to_s3',
        bash_command='python /opt/airflow/src/upload_to_s3.py',
    )

    ingest_from_s3 = BashOperator(
        task_id='ingest_from_s3_to_postgres',
        bash_command='python /opt/airflow/src/ingest_from_s3_to_postgres.py',
    )

    run_dbt_models = BashOperator(
        task_id='run_dbt_models',
        bash_command='cd /opt/airflow/dbt/youtube && dbt run',
    )

    run_dbt_tests = BashOperator(
        task_id='run_dbt_tests',
        bash_command='cd /opt/airflow/dbt/youtube && dbt test',
    )

    upload_to_s3 >> ingest_from_s3 >> run_dbt_models >> run_dbt_tests

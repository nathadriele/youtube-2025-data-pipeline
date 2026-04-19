install:
	pip install -r requirements.txt

run-upload:
	python src/upload_to_s3.py

run-ingest:
	python src/ingest_from_s3_to_postgres.py

test-s3:
	python dev/test_s3_connection.py

dbt-run:
	dbt run --project-dir dbt/youtube --profiles-dir .

dbt-test:
	dbt test --project-dir dbt/youtube --profiles-dir .
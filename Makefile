.PHONY: help install docker-up docker-down run-upload run-ingest test-s3 test dbt-run dbt-test dbt-deps dbt-seed dbt-snapshot

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

docker-up: ## Build and start all Docker containers (requires .env configured)
	docker-compose up --build -d

docker-down: ## Stop and remove all Docker containers
	docker-compose down

run-upload: ## Upload CSV data to AWS S3
	python src/upload_to_s3.py

run-ingest: ## Ingest data from S3 into PostgreSQL
	python src/ingest_from_s3_to_postgres.py

test-s3: ## Test AWS S3 connectivity
	python dev/test_s3_connection.py

test: ## Run Python unit tests with pytest
	pytest tests/ -v

dbt-deps: ## Install dbt dependencies
	dbt deps --project-dir dbt/youtube --profiles-dir .

dbt-seed: ## Load dbt seed reference data
	dbt seed --project-dir dbt/youtube --profiles-dir .

dbt-run: ## Run dbt models
	dbt run --project-dir dbt/youtube --profiles-dir .

dbt-test: ## Run dbt tests
	dbt test --project-dir dbt/youtube --profiles-dir .

dbt-snapshot: ## Run dbt snapshots
	dbt snapshot --project-dir dbt/youtube --profiles-dir .

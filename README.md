# YouTube Data Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Airflow](https://img.shields.io/badge/Airflow-2.8.1-green)
![dbt](https://img.shields.io/badge/dbt-1.5.9-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Metabase](https://img.shields.io/badge/Metabase-0.49.13-509EE3)
![Tests](https://img.shields.io/badge/Pytest-19%20passed-success)

A modular and scalable Data Engineering project that ingests YouTube channel performance data, stores it in AWS S3 and PostgreSQL, transforms it with dbt, orchestrates workflows with Apache Airflow, and visualizes analytics through Metabase dashboards.

Built following modern Data Engineering best practices: reproducibility, observability, modularity, and cloud integration.

---

## Problem Statement

This project analyzes YouTube channel performance metrics to answer key business questions:

- Which **metaverse integration levels** correlate with higher subscriber counts?
- How does **neural interface compatibility** affect engagement scores?
- Who are the **top-performing creators** ranked by subscribers and engagement?
- What are the **average content value indices** across different channel categories?

The pipeline automates the end-to-end flow — from raw CSV ingestion to a clean, tested analytical model — enabling self-service analytics through Metabase.

---

## Dataset

The source dataset (`data/youtube_2025_dataset.csv`) contains **5,000 records** of YouTube channel metrics with 14 original columns. The pipeline selects **8 core columns** for analysis:

| Column | Type | Description |
|--------|------|-------------|
| `channel_name` | text | Name of the YouTube channel |
| `youtuber` | text | Creator display name |
| `subscribers` | bigint | Total subscriber count |
| `total_videos` | bigint | Total videos published |
| `engagement_score` | bigint | Engagement metric score |
| `content_value_index` | bigint | Content value rating |
| `metaverse_integration_level` | text | Level of metaverse integration (Full, Advanced, Partial, Basic, None) |
| `neural_interface_compatible` | text | Neural interface compatibility (True/False) |

---

## Tech Stack

| Stage | Tool | Purpose |
|-------|------|---------|
| **Storage** | AWS S3 | Cloud object storage for raw CSV data |
| **Database** | PostgreSQL 13 | Data warehouse for raw and transformed data |
| **Ingestion** | Python, boto3, psycopg2 | S3 upload and PostgreSQL bulk load |
| **Transformation** | dbt 1.5.9 | SQL-based modeling with staging/marts pattern |
| **Orchestration** | Apache Airflow 2.8.1 | DAG scheduling, retries, and dependency management |
| **Visualization** | Metabase 0.49 | Interactive dashboards and data exploration |
| **Infrastructure** | Docker Compose | Containerized multi-service environment |
| **Testing** | dbt tests + Pytest | Data validation (custom SQL tests + 19 unit tests) |
| **Config** | dotenv (.env) | Secure credential management |

---

## Data Pipeline

The pipeline follows a standard batch ELT (Extract-Load-Transform) architecture:

```
┌─────────────┐     ┌──────────┐     ┌────────────┐     ┌──────────────┐     ┌──────────┐
│  CSV Dataset │────>│  AWS S3  │────>│ PostgreSQL │────>│  dbt Models  │────>│ Metabase │
│  (5K rows)   │     │ (Raw)    │     │ (Raw + DW) │     │ (Staging +   │     │Dashboard │
│              │     │          │     │            │     │  Marts)      │     │          │
└─────────────┘     └──────────┘     └────────────┘     └──────────────┘     └──────────┘
       │                   │                │                    │
       │              upload_to_s3    ingest_from_s3       dbt run + test
       │              (boto3)         (psycopg2 + COPY)    (staging/marts)
       │                                                                      │
       └──────────── Orchestrated by Apache Airflow (4 DAGs) ────────────────┘
```

### Step-by-step flow:

1. **Extract** — `upload_to_s3.py` uploads the local CSV to an AWS S3 bucket
2. **Load** — `ingest_from_s3_to_postgres.py` reads the CSV from S3, transforms column names/types, and bulk-loads into PostgreSQL (`youtube_2025_dataset`)
3. **Transform** — dbt builds a staging view (`stg_youtube_data`) and 4 mart tables with aggregation and ranking logic
4. **Validate** — dbt runs schema tests (not_null, unique, custom SQL assertions) and Airflow runs data quality checks
5. **Visualize** — Metabase connects to PostgreSQL and renders interactive dashboards

---

## dbt Models

### Staging Layer

| Model | Materialization | Description |
|-------|----------------|-------------|
| `stg_youtube_data` | view | Clean pass-through of source data with explicit column selection and type normalization |

### Marts Layer

| Model | Materialization | Granularity | Description |
|-------|----------------|-------------|-------------|
| `youtube_summary` | table | metaverse_integration_level × neural_interface_compatible | Cross-dimensional aggregation with avg subscribers and engagement |
| `youtube_category_summary` | table | metaverse_integration_level | Aggregation by metaverse level with avg/max subscribers and engagement |
| `youtube_neural_summary` | table | neural_interface_compatible | Aggregation by neural interface status with avg/max subscribers and engagement |
| `youtube_top_creators` | table | youtuber (row-level) | Ranked list of all creators ordered by subscribers and engagement score |

### Supporting Assets

| Type | Asset | Description |
|------|-------|-------------|
| **Seed** | `metaverse_levels` | Reference table with 5 levels, descriptions, and sort order |
| **Snapshot** | `snap_youtube_top_creators` | SCD Type 2 change tracking on subscriber counts and engagement |
| **Macros** | `clean_text`, `percentile`, `generate_surrogate_key` | Reusable SQL helpers |
| **Analyses** | `engagement_distribution_by_metaverse`, `subscriber_vs_engagement_correlation` | Ad-hoc analytical queries |

---

## Orchestration (Airflow)

The main DAG orchestrates the full ETL flow:

![DAG Graph](https://github.com/user-attachments/assets/f3df376d-d8d4-4a47-9d18-1d8906077b64)

### DAG: `youtube_data_pipeline` (main ETL)

```
upload_to_s3 >> ingest_from_s3 >> run_dbt_models >> run_dbt_tests
```

| Task | Operator | Description |
|------|----------|-------------|
| `upload_to_s3` | BashOperator | Uploads CSV to S3 via Python script |
| `ingest_from_s3` | BashOperator | Reads from S3, loads into PostgreSQL via COPY |
| `run_dbt_models` | BashOperator | Builds all dbt staging + mart models |
| `run_dbt_tests` | BashOperator | Runs all dbt schema and custom tests |

### DAG: `youtube_data_quality_pipeline`

```
check_raw_table_rows >> check_raw_not_null_columns >> check_mart_table_rows
```

Validates row counts and NOT NULL constraints on key columns (`youtuber`, `subscribers`, `engagement_score`).

### DAG: `youtube_pipeline_monitoring`

```
check_required_tables_exist >> monitor_raw_table_volume >> monitor_negative_values >> monitor_mart_table_volume
```

Operational checks for table existence, row volume thresholds (configurable via env vars), and negative value detection.

### DAG: `youtube_validation_pipeline`

```
test_s3_connection >> test_postgres_connection
```

Infrastructure connectivity validation before pipeline runs.

All DAGs are scheduled `@daily` with `catchup=False` and configured retries with delay.

---

## Dashboard (Metabase)

Metabase connects directly to the PostgreSQL data warehouse and provides interactive visualizations.

![Dashboard Overview](https://github.com/user-attachments/assets/a466e13b-561b-40d8-8e8c-5e2f7a45574a)

| Tile | Source Model | Description |
|------|-------------|-------------|
| **Top Categories** | `youtube_category_summary` | Bar chart of creator count and avg subscribers by metaverse integration level |
| **Engagement vs. Subscribers** | `youtube_top_creators` | Scatter plot showing correlation between subscriber count and engagement score |
| **Engagement Analysis** | `youtube_summary` | Aggregated engagement metrics by metaverse level and neural interface status |
| **Subscriber Distribution** | `youtube_neural_summary` | Comparison of subscriber statistics between neural-compatible and non-compatible channels |

![Top Categories](https://github.com/user-attachments/assets/8c35b152-42e0-41f2-ae81-4ee040ba81cc)

![Engagement vs Subscribers](https://github.com/user-attachments/assets/bc057502-db37-46b1-a542-9fbbe4cc98f7)

![Engagement Analysis](https://github.com/user-attachments/assets/05b93b0b-8af7-4391-b7bd-a86e2093f9b7)

![Subscriber Distribution](https://github.com/user-attachments/assets/2ea4707f-63d0-4fc7-b50c-ccd2fccc0d2d)

---

## Tests & Validation

The project implements data quality at three levels:

### 1. Python Unit Tests (Pytest — 19 tests)

```bash
make test
```

| Test Module | Tests | What it validates |
|-------------|-------|-------------------|
| `test_data_quality.py` | 7 | CSV existence, size, columns, row count, nulls, positive numerics |
| `test_transform.py` | 7 | Column selection, renaming, whitespace stripping, type conversion, NaN handling, dedup, error on missing cols |
| `test_config.py` | 5 | Config loading, required env vars, default values, error on missing vars |

### 2. dbt Schema Tests

Defined in `youtube_marts.yml`, `youtube_summary.yml`, and `stg_youtube_data.yml`:

- **not_null** on all key columns (youtuber, subscribers, engagement_score, metaverse_integration_level, etc.)
- **unique** on dimension columns (metaverse_integration_level in category_summary, neural_interface_compatible in neural_summary)

### 3. dbt Custom SQL Tests (4 assertions)

| Test | File | Rule |
|------|------|------|
| `assert_positive_engagement` | `tests/` | All engagement scores must be > 0 |
| `assert_subscribers_within_range` | `tests/` | No subscriber count exceeds 1 billion |
| `assert_valid_metaverse_levels` | `tests/` | Only accepted values (Full, Advanced, Partial, Basic, None, Unknown) |
| `assert_valid_neural_interface` | `tests/` | Only accepted values (True, False, Yes, No, Unknown) |

### 4. Airflow Runtime Checks

- `youtube_data_quality_pipeline`: row counts + NOT NULL validation at runtime
- `youtube_pipeline_monitoring`: table existence, volume thresholds, negative value detection

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)
- An [AWS account](https://aws.amazon.com/) with S3 access and programmatic credentials

### Step 1: Clone the repository

```bash
git clone https://github.com/<your-username>/youtube-2025-data-pipeline.git
cd youtube-2025-data-pipeline
```

### Step 2: Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials. All fields are required:

```bash
# AWS Configuration
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
S3_FILE_KEY=youtube_2025_dataset.csv
LOCAL_FILE_PATH=data/youtube_2025_dataset.csv

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=youtube_db
DB_NAME=youtube_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db          # Use "db" inside Docker, "localhost" for local dev
DB_PORT=5432
```

### Step 3: Build and start all services

```bash
make docker-up
```

This builds a custom Airflow image with all Python dependencies pre-installed (`requirements.txt`) and starts 5 services:

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Data warehouse |
| Airflow Webserver | 8080 | DAG management UI |
| Airflow Scheduler | — | Task execution engine |
| Airflow Init | — | Database initialization (runs once) |
| Metabase | 3000 | BI dashboard |

### Step 4: Access the services

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow UI | http://localhost:8080 | `airflow` / `airflow` |
| Metabase | http://localhost:3000 | Configure on first access |

### Step 5: Run the pipeline

1. Open Airflow at http://localhost:8080
2. Toggle the `youtube_data_pipeline` DAG to **unpaused**
3. Click **Trigger DAG** for a manual run, or wait for the daily schedule

### Step 6: Explore the dashboard

1. Open Metabase at http://localhost:3000
2. Complete initial setup — connect to PostgreSQL using:
   - Host: `db` / Port: `5432` / Database: (your `POSTGRES_DB`)
3. Build or explore dashboards with the transformed tables (`youtube_summary`, `youtube_category_summary`, `youtube_neural_summary`, `youtube_top_creators`)

### Step 7: Run tests (optional)

```bash
# Python unit tests
make test

# dbt tests (requires running pipeline first)
make dbt-test
```

---

## Reproducibility

This project is designed to be fully reproducible with a single command sequence:

```bash
git clone https://github.com/<your-username>/youtube-2025-data-pipeline.git
cd youtube-2025-data-pipeline
cp .env.example .env   # Fill in your credentials
make docker-up          # Builds and starts everything
```

Key reproducibility features:

- **Dockerfile** — custom Airflow image with all Python dependencies baked in
- **docker-compose.yml** — orchestrates PostgreSQL, Airflow (webserver + scheduler), and Metabase with health checks and dependency ordering
- **`.env.example`** — complete template with inline documentation for every variable
- **Makefile** — one-command targets for every pipeline operation (`make help` to list all)
- **Dataset included** — `data/youtube_2025_dataset.csv` is committed to the repository (5000 rows, 650KB)
- **dbt models** — all SQL transformations are version-controlled and deterministic

---

## Project Structure

```
.
├── dags/                                        # Airflow DAG definitions
│   ├── youtube_data_pipeline_dag.py             # Main ETL pipeline (4 tasks)
│   ├── youtube_data_quality_pipeline_dag.py     # Data quality validation
│   ├── youtube_pipeline_monitoring_dag.py       # Operational monitoring
│   └── youtube_validation_pipeline_dag.py       # Infrastructure connectivity
├── data/
│   └── youtube_2025_dataset.csv                 # Source dataset (5000 rows)
├── dbt/youtube/
│   ├── dbt_project.yml                          # dbt project configuration
│   ├── packages.yml                             # dbt package dependencies (dbt_utils)
│   ├── models/
│   │   ├── sources.yml                          # Source table definition
│   │   ├── staging/
│   │   │   ├── stg_youtube_data.sql             # Staging view (raw → clean)
│   │   │   └── stg_youtube_data.yml             # Staging schema + tests
│   │   └── marts/
│   │       ├── youtube_summary.sql              # Aggregation: metaverse × neural
│   │       ├── youtube_summary.yml              # Schema + tests for summary
│   │       ├── youtube_category_summary.sql     # Aggregation: metaverse level
│   │       ├── youtube_neural_summary.sql       # Aggregation: neural interface
│   │       ├── youtube_top_creators.sql         # Ranked creators
│   │       └── youtube_marts.yml                # Schema + tests for all marts
│   ├── macros/
│   │   ├── clean_text.sql                       # Text normalization macro
│   │   ├── generate_surrogate_key.sql           # MD5 surrogate key generator
│   │   └── percentile.sql                       # Percentile calculation macro
│   ├── seeds/
│   │   ├── metaverse_levels.csv                 # Reference data (5 levels)
│   │   └── metaverse_levels.yml                 # Seed schema + tests
│   ├── tests/                                   # Custom dbt SQL tests
│   │   ├── assert_positive_engagement.sql
│   │   ├── assert_subscribers_within_range.sql
│   │   ├── assert_valid_metaverse_levels.sql
│   │   └── assert_valid_neural_interface.sql
│   ├── analyses/                                # Ad-hoc analytical queries
│   │   ├── engagement_distribution_by_metaverse.sql
│   │   └── subscriber_vs_engagement_correlation.sql
│   └── snapshots/
│       └── snap_youtube_top_creators.sql        # SCD Type 2 change tracking
├── dev/
│   ├── test_s3_connection.py                    # AWS S3 connectivity test
│   └── test_postgres_connection.py              # PostgreSQL connectivity test
├── src/
│   ├── upload_to_s3.py                          # CSV → S3 upload script
│   └── ingest_from_s3_to_postgres.py            # S3 → PostgreSQL ingestion (COPY)
├── tests/                                       # Python unit tests (pytest)
│   ├── conftest.py                              # Shared test fixtures
│   ├── test_data_quality.py                     # CSV integrity tests (7)
│   ├── test_transform.py                        # Transform logic tests (7)
│   └── test_config.py                           # Config loading tests (5)
├── images/                                      # Architecture diagrams
│   ├── dag.png                                  # Pipeline architecture diagram
│   └── orchestration.png                        # Orchestration diagram
├── Dockerfile                                   # Custom Airflow image (deps pre-installed)
├── docker-compose.yml                           # Multi-service orchestration (5 services)
├── profiles.yml                                 # dbt PostgreSQL connection profile
├── requirements.txt                             # Python dependencies
├── Makefile                                     # Build and run convenience commands
├── .env.example                                 # Environment variable template
└── .gitignore
```

---

## Makefile Commands

```
make help          # Show all available commands
make install       # Install Python dependencies locally
make docker-up     # Build and start all Docker containers
make docker-down   # Stop and remove all containers
make test          # Run Python unit tests (pytest, 19 tests)
make dbt-deps      # Install dbt package dependencies
make dbt-seed      # Load reference seed data into PostgreSQL
make dbt-run       # Build all dbt models (staging + marts)
make dbt-test      # Run all dbt schema and custom tests
make dbt-snapshot  # Run dbt snapshots (SCD Type 2)
```

---

## Future Improvements

- **Terraform / IaC** — provision AWS S3 bucket and IAM roles with infrastructure-as-code for full cloud reproducibility
- **Incremental ingestion** — replace TRUNCATE with upsert logic for scaling beyond the current dataset
- **Partitioning** — add table partitioning in PostgreSQL (or migrate to BigQuery) for larger datasets
- **CI/CD** — add GitHub Actions for automated testing on push/PR
- **Streaming** — integrate Kafka or Pub/Sub for real-time data ingestion
- **dbt version upgrade** — migrate from dbt 1.5.9 to 1.8+ for latest features

---

## Contributing

Feel free to fork, enhance, or contribute! Open a PR or issue.

# YouTube 2025 Data Pipeline

A modular, and scalable end-to-end Data Engineering project that ingests video performance data from the YouTube 2025 Dataset, stores it in AWS S3 and PostgreSQL, transforms the data using dbt, orchestrates all steps with Apache Airflow, and provides dynamic visualizations with Metabase.

This project was structured following best practices of modern Data Engineering, enabling reproducibility, observability, modularity, and ease of future integration with cloud services.

## Objective

To build a professional-grade ETL pipeline that:

- ✅ Ingests raw CSV data into AWS S3 and PostgreSQL
- ✅ Transforms and models the data using dbt
- ✅ Automates the pipeline using Apache Airflow
- ✅ Visualizes YouTube analytics through Metabase dashboards
- ✅ Ensures a modular, testable, and well-documented architecture

## Tools & Technologies

| Stage          | Tool / Technology      | Purpose                                  |
| -------------- | ---------------------- | ---------------------------------------- |
| Ingestion      | Python, boto3          | Upload raw data to AWS S3                |
| Ingestion      | Python, psycopg2       | Load data from S3 to PostgreSQL          |
| Transformation | dbt (data build tool)  | SQL-based modeling and cleaning          |
| Orchestration  | Apache Airflow         | Task scheduling and ETL orchestration    |
| Infrastructure | Docker, Docker Compose | Containerization and environment control |
| Storage        | AWS S3, PostgreSQL     | Raw and processed data persistence       |
| Visualization  | Metabase               | Dashboards and data exploration          |
| Testing        | dbt tests, Pytest      | Data validation and ingestion testing    |
| Config         | dotenv (.env)          | Secure credential management             |

## Pipeline Architecture

### Ingestion:

- Raw YouTube dataset (CSV) is uploaded to AWS S3 using the `upload_to_s3.py` script
- `ingest_from_s3_to_postgres.py` reads the S3 file and loads it into a PostgreSQL table

### Transformation:

- dbt transforms the raw table into clean staging and mart models
Examples:
   - `stg_youtube_data`: cleans and normalizes column types
   - `youtube_summary`: aggregates insights such as total views, likes, duration, and engagement metrics

### Orchestration: 

The DAG below orchestrates the full flow:

![image](https://github.com/user-attachments/assets/f3df376d-d8d4-4a47-9d18-1d8906077b64)

- Metabase reads from PostgreSQL
- KPIs and metrics visualized as:
   - Top Categories
   - Views by Country
   - Engagement Analysis
   - Views per Subscriber

## Dashboard

Includes:
- Total Views
- Engagement Score
- Top Performing Categories
- Subscriber Growth
- Views Distribution

## Airflow DAG

### DAG:

- `upload_to_s3`: pushes CSV to AWS S3
- `ingest_from_s3`: reads from S3 and writes to PostgreSQL
- `run_dbt_models`: transforms raw data into analytics models
- `run_dbt_tests`: ensures constraints and integrity

### DAG configuration:

- Scheduled daily
- Retries + failure handling
- Defined task dependencies

## Key Metrics Extracted

![image](https://github.com/user-attachments/assets/9c121cb4-5946-4253-adcf-11302eb1b682)

### 📈 Top Categories

![image](https://github.com/user-attachments/assets/bc057502-db37-46b1-a542-9fbbe4cc98f7)

### 📈 Views by Country

![views_by_country](https://github.com/user-attachments/assets/0b32397e-d95d-46fc-b136-b49460c7d0c9)

### 📈 Engagement vs. Views

![image](https://github.com/user-attachments/assets/05b93b0b-8af7-4391-b7bd-a86e2093f9b7)

### 📈 Views per Subscriber

![image](https://github.com/user-attachments/assets/2ea4707f-63d0-4fc7-b50c-ccd2fccc0d2d)

## Tests & Validation

- Pytest: Validates core scripts like S3 and PostgreSQL ingestion
- dbt tests:
   - Column constraints (e.g., `not_null`, `unique`)
   - Data consistency and business rules
 
## Environment Configuration

- `.env` file is used to store credentials:
  
![image](https://github.com/user-attachments/assets/59ad9315-349d-41e9-bb02-e60253e6014e)

## Getting Started

```py
git clone https://github.com/your-username/youtube-2025-data-pipeline.git
cd youtube-2025-data-pipeline
```

#### 1. Configure `.env`
#### 2. Run Docker Compose:

```py
docker-compose up --build
```

#### 3. Access services:

- Airflow: `http://localhost:8080`
- Metabase: `http://localhost:3000`

#### 4. Trigger the DAG and explore dashboards

## Highlights

- Modular and production-ready
- Integrates with AWS S3 + PostgreSQL
- SQL-modeling using dbt
- Automated orchestration via Airflow
- Dashboard-ready insights with Metabase

## Contributing

Feel free to fork, enhance or contribute! Open a PR or issue and let’s build this together, my friend! 

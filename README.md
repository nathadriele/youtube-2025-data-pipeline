# YouTube 2025 Data Pipeline

A modular and scalable Data Engineering project designed to ingest video performance data from the YouTube 2025 Dataset, store it securely in AWS S3 and PostgreSQL, transform it through dbt, orchestrate workflows using Apache Airflow, and deliver dynamic visualizations with Metabase.

Structured according to modern Data Engineering best practices, this project ensures reproducibility, observability, modularity, and seamless future integration with cloud services, providing a robust and extensible foundation for data-driven initiatives.

![Captura de tela 2025-04-13 171618](https://github.com/user-attachments/assets/72dfbb65-f0a4-42a9-8c61-42367703a700)

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

![metabase](https://github.com/user-attachments/assets/a466e13b-561b-40d8-8e8c-5e2f7a45574a)

### 📈 Top Categories

![image](https://github.com/user-attachments/assets/8c35b152-42e0-41f2-ae81-4ee040ba81cc)

### 📈 Views by Country

![image](https://github.com/user-attachments/assets/bc057502-db37-46b1-a542-9fbbe4cc98f7)

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

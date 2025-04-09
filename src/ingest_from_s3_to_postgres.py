import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import boto3
from io import StringIO

# Load environment variables
load_dotenv()

# S3 details
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FILE_KEY = os.getenv("S3_FILE_KEY")

# PostgreSQL details
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to S3 and read the CSV
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

csv_obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_KEY)
csv_data = csv_obj['Body'].read().decode('utf-8')
df = pd.read_csv(StringIO(csv_data))

# Connect to PostgreSQL and upload data
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# Create table if not exists
create_table_query = """
CREATE TABLE IF NOT EXISTS youtube_2025_dataset (
    "Youtuber" TEXT,
    "Subscribers" BIGINT,
    "Video views" BIGINT,
    "Category" TEXT,
    "Country" TEXT
);
"""
cursor.execute(create_table_query)
conn.commit()

# Upload data using COPY
buffer = StringIO()
df.to_csv(buffer, index=False, header=False)
buffer.seek(0)

cursor.copy_expert("COPY youtube_2025_dataset FROM STDIN WITH (FORMAT CSV)", buffer)
conn.commit()

cursor.close()
conn.close()
print("Data loaded successfully into PostgreSQL!")

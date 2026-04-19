"""
Test fixtures shared across all test modules.
"""
import os
import sys
import pytest

# Add project root directories to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "dev"))


@pytest.fixture
def sample_csv_path():
    """Return the path to the sample dataset CSV."""
    return os.path.join(PROJECT_ROOT, "data", "youtube_2025_dataset.csv")


@pytest.fixture
def sample_csv_columns():
    """Return the expected column names in the raw CSV (before transformation)."""
    return [
        "Channel Name",
        "Youtuber Name",
        "Total Videos",
        "Best Video",
        "Avg Video Length (min)",
        "Total Subscribers",
        "Members Count",
        "AI Generated Content (%)",
        "Neural Interface Compatible",
        "Metaverse Integration Level",
        "Quantum Computing Topics",
        "Holographic Content Rating",
        "Engagement Score",
        "Content Value Index",
    ]


@pytest.fixture
def expected_pipeline_columns():
    """Return the column names expected after pipeline transformation."""
    return [
        "channel_name",
        "youtuber",
        "subscribers",
        "total_videos",
        "engagement_score",
        "content_value_index",
        "metaverse_integration_level",
        "neural_interface_compatible",
    ]


@pytest.fixture
def env_vars_keys():
    """Return the required environment variable keys for the pipeline."""
    return [
        "AWS_ACCESS_KEY",
        "AWS_SECRET_KEY",
        "S3_BUCKET_NAME",
        "S3_FILE_KEY",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
    ]

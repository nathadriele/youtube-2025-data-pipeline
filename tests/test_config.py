"""
Tests for configuration loading functions.
Validates that config loaders properly read env vars and raise on missing values.
"""
import os
import pytest
from unittest.mock import patch


def test_upload_config_requires_aws_keys():
    """Verify that upload_to_s3 raises ValueError when AWS keys are missing."""
    from upload_to_s3 import load_config

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Missing required environment variables"):
            load_config()


def test_upload_config_returns_expected_keys():
    """Verify that load_config returns all expected keys when env vars are set."""
    from upload_to_s3 import load_config

    env = {
        "AWS_ACCESS_KEY": "test-key",
        "AWS_SECRET_KEY": "test-secret",
        "S3_BUCKET_NAME": "test-bucket",
        "S3_FILE_KEY": "test-file.csv",
        "LOCAL_FILE_PATH": "/tmp/test.csv",
    }
    with patch.dict(os.environ, env, clear=True):
        config = load_config()
        assert config["aws_access_key"] == "test-key"
        assert config["aws_secret_key"] == "test-secret"
        assert config["s3_bucket_name"] == "test-bucket"


def test_ingest_config_requires_all_vars():
    """Verify that ingest config raises ValueError when any variable is missing."""
    from ingest_from_s3_to_postgres import load_config

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Missing required environment variables"):
            load_config()


def test_ingest_config_returns_expected_keys():
    """Verify that ingest load_config returns all expected keys."""
    from ingest_from_s3_to_postgres import load_config

    env = {
        "AWS_ACCESS_KEY": "test-key",
        "AWS_SECRET_KEY": "test-secret",
        "S3_BUCKET_NAME": "test-bucket",
        "S3_FILE_KEY": "test-file.csv",
        "DB_NAME": "testdb",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
    }
    with patch.dict(os.environ, env, clear=True):
        config = load_config()
        assert config["db_name"] == "testdb"
        assert config["db_host"] == "localhost"
        assert config["db_port"] == "5432"


def test_db_port_defaults_to_5432():
    """Verify DB_PORT defaults to 5432 when not set."""
    from ingest_from_s3_to_postgres import load_config

    env = {
        "AWS_ACCESS_KEY": "test-key",
        "AWS_SECRET_KEY": "test-secret",
        "S3_BUCKET_NAME": "test-bucket",
        "S3_FILE_KEY": "test-file.csv",
        "DB_NAME": "testdb",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
        "DB_HOST": "localhost",
    }
    with patch.dict(os.environ, env, clear=True):
        config = load_config()
        assert config["db_port"] == "5432"

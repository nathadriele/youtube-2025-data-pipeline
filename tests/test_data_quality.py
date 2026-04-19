"""
Tests for the raw dataset integrity and structure.
Validates that the CSV file exists, is not empty, has the expected columns,
and contains valid data.
"""
import pandas as pd
import pytest


def test_csv_file_exists(sample_csv_path):
    """Verify that the raw CSV dataset file exists."""
    import os
    assert os.path.isfile(sample_csv_path), f"Dataset CSV not found at {sample_csv_path}"


def test_csv_file_not_empty(sample_csv_path):
    """Verify that the raw CSV file is not empty."""
    import os
    file_size = os.path.getsize(sample_csv_path)
    assert file_size > 0, "Dataset CSV file is empty"


def test_csv_has_expected_columns(sample_csv_path, sample_csv_columns):
    """Verify that the CSV has all 14 expected columns."""
    df = pd.read_csv(sample_csv_path, nrows=1)
    for col in sample_csv_columns:
        assert col in df.columns, f"Missing expected column: '{col}'"


def test_csv_has_data_rows(sample_csv_path):
    """Verify that the CSV has actual data rows (not just header)."""
    df = pd.read_csv(sample_csv_path)
    assert len(df) > 0, "CSV has no data rows"


def test_csv_row_count_matches_expectation(sample_csv_path):
    """Verify the CSV has approximately 5000 rows."""
    df = pd.read_csv(sample_csv_path)
    assert 4500 <= len(df) <= 5500, (
        f"Expected ~5000 rows, got {len(df)}"
    )


def test_no_fully_null_columns(sample_csv_path):
    """Verify no column is entirely null."""
    df = pd.read_csv(sample_csv_path)
    null_counts = df.isnull().sum()
    fully_null = null_counts[null_counts == len(df)]
    assert len(fully_null) == 0, (
        f"Fully null columns found: {list(fully_null.index)}"
    )


def test_key_numeric_columns_are_valid(sample_csv_path):
    """Verify that key numeric columns contain positive values."""
    df = pd.read_csv(sample_csv_path)
    numeric_cols = [
        "Total Subscribers",
        "Total Videos",
        "Engagement Score",
        "Content Value Index",
    ]
    for col in numeric_cols:
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        assert (values >= 0).all(), f"Negative values found in column '{col}'"

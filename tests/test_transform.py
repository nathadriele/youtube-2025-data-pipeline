"""
Tests for the data transformation pipeline (src/ingest_from_s3_to_postgres.py).
Validates the transform_dataframe function produces correct output.
"""
import pandas as pd
import pytest

from ingest_from_s3_to_postgres import transform_dataframe


@pytest.fixture
def sample_raw_df():
    """Create a small sample DataFrame mimicking the raw CSV structure."""
    return pd.DataFrame({
        "Channel Name": ["Test Channel A", "Test Channel B", "Test Channel C"],
        "Youtuber Name": ["Alice", "Bob", "Charlie"],
        "Total Videos": [100, 200, 300],
        "Best Video": ["Video1", "Video2", "Video3"],
        "Avg Video Length (min)": [10.5, 15.0, 20.3],
        "Total Subscribers": [500000, 1200000, 800000],
        "Members Count": [1000, 2000, 3000],
        "AI Generated Content (%)": [10, 50, 90],
        "Neural Interface Compatible": ["True", "False", "True"],
        "Metaverse Integration Level": ["Full", "None", "Advanced"],
        "Quantum Computing Topics": [3, 7, 1],
        "Holographic Content Rating": ["3D", "2D", "3D"],
        "Engagement Score": [95.5, 42.3, 78.1],
        "Content Value Index": [8.5, 5.0, 7.2],
    })


def test_transform_selects_correct_columns(sample_raw_df, expected_pipeline_columns):
    """Verify that transform_dataframe selects only the 8 expected columns."""
    result = transform_dataframe(sample_raw_df)
    assert list(result.columns) == expected_pipeline_columns


def test_transform_renames_columns_correctly(sample_raw_df):
    """Verify column renaming (e.g., Total Subscribers -> subscribers)."""
    result = transform_dataframe(sample_raw_df)
    assert "youtuber" in result.columns
    assert "subscribers" in result.columns
    assert "Youtuber Name" not in result.columns
    assert "Total Subscribers" not in result.columns


def test_transform_strips_whitespace(sample_raw_df):
    """Verify that text columns have whitespace stripped."""
    df_with_spaces = sample_raw_df.copy()
    df_with_spaces["Channel Name"] = ["  Test A  ", " Test B ", "Test C  "]
    result = transform_dataframe(df_with_spaces)
    assert result["channel_name"].iloc[0] == "Test A"


def test_transform_converts_numeric_types(sample_raw_df):
    """Verify that numeric columns are properly converted to int64."""
    result = transform_dataframe(sample_raw_df)
    assert result["subscribers"].dtype == "int64"
    assert result["total_videos"].dtype == "int64"
    assert result["engagement_score"].dtype == "int64"
    assert result["content_value_index"].dtype == "int64"


def test_transform_handles_nan_numeric_values():
    """Verify that NaN numeric values are coerced to 0."""
    df_with_nan = pd.DataFrame({
        "Channel Name": ["Test"],
        "Youtuber Name": ["Alice"],
        "Total Videos": [10],
        "Best Video": ["Video1"],
        "Avg Video Length (min)": [5.0],
        "Total Subscribers": [None],
        "Members Count": [100],
        "AI Generated Content (%)": [0],
        "Neural Interface Compatible": ["True"],
        "Metaverse Integration Level": ["Full"],
        "Quantum Computing Topics": [0],
        "Holographic Content Rating": ["2D"],
        "Engagement Score": [50.0],
        "Content Value Index": [5.0],
    })
    result = transform_dataframe(df_with_nan)
    assert result["subscribers"].iloc[0] == 0


def test_transform_removes_duplicates():
    """Verify that duplicate rows are removed."""
    df_dup = pd.DataFrame({
        "Channel Name": ["Test A", "Test A"],
        "Youtuber Name": ["Alice", "Alice"],
        "Total Videos": [10, 10],
        "Best Video": ["V1", "V1"],
        "Avg Video Length (min)": [5.0, 5.0],
        "Total Subscribers": [100, 100],
        "Members Count": [50, 50],
        "AI Generated Content (%)": [0, 0],
        "Neural Interface Compatible": ["True", "True"],
        "Metaverse Integration Level": ["Full", "Full"],
        "Quantum Computing Topics": [0, 0],
        "Holographic Content Rating": ["2D", "2D"],
        "Engagement Score": [50.0, 50.0],
        "Content Value Index": [5.0, 5.0],
    })
    result = transform_dataframe(df_dup)
    assert len(result) == 1


def test_transform_raises_on_missing_columns():
    """Verify that transform raises ValueError when expected columns are missing."""
    df_missing = pd.DataFrame({
        "Channel Name": ["Test"],
        "Youtuber Name": ["Alice"],
    })
    with pytest.raises(ValueError, match="Missing expected columns"):
        transform_dataframe(df_missing)

"""Data loading and validation for the student dashboard."""

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_FILE = Path(__file__).parent / "data" / "student_data_clean.csv"
EXPECTED_COLUMNS = ["student_id", "unique_name", "name", "gender", "grade", "math", "science", "english", "total"]
SUBJECTS = ["math", "science", "english"]


def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate the presentation dataset and return it unchanged."""
    if len(data) != 4000:
        raise ValueError(f"Expected 4,000 rows, found {len(data):,}.")
    if list(data.columns) != EXPECTED_COLUMNS:
        raise ValueError("Unexpected columns. Expected: " + ", ".join(EXPECTED_COLUMNS))
    if data["student_id"].isna().any() or not data["student_id"].is_unique:
        raise ValueError("student_id must be present and unique for every row.")
    if data["unique_name"].isna().any() or not data["unique_name"].is_unique:
        raise ValueError("unique_name must be present and unique for every row.")
    if not data["grade"].between(1, 12).all():
        raise ValueError("grade values must be integers from 1 through 12.")
    if not data[SUBJECTS].apply(lambda column: column.between(0, 100).all()).all():
        raise ValueError("Subject scores must be between 0 and 100.")
    if not data["total"].between(0, 300).all():
        raise ValueError("total values must be between 0 and 300.")
    if not (data["total"] == data[SUBJECTS].sum(axis=1)).all():
        raise ValueError("Every total must equal math + science + english.")
    return data


@st.cache_data
def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the cleaned CSV and validate its schema and value ranges."""
    return validate_data(pd.read_csv(path))
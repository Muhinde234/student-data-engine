"""Upload, clean, and validate datasets for the student dashboard."""

from typing import Any

import pandas as pd
import streamlit as st


EXPECTED_COLUMNS = ["student_id", "unique_name", "name", "gender", "grade", "math", "science", "english", "total"]
SUBJECTS = ["math", "science", "english"]
SOURCE_COLUMNS = ["name", "gender", "grade", "math", "science", "english", "total"]


def _column_key(value: Any) -> str:
    return "".join(character for character in str(value).lower() if character.isalnum())


def _clean_text(series: pd.Series, fallback: str) -> pd.Series:
    """Remove wrapping quotes and normalize whitespace in text fields."""
    cleaned = series.fillna(fallback).astype(str).str.strip()
    return cleaned.str.replace(r"^[\"']+|[\"']+$", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()


def _read_upload(uploaded_file: Any) -> pd.DataFrame:
    """Read a CSV whether it has a standard header or not."""
    uploaded_file.seek(0)
    frame = pd.read_csv(uploaded_file)
    normalized_columns = {_column_key(column): column for column in frame.columns}
    expected_keys = {_column_key(column) for column in SOURCE_COLUMNS}
    if not expected_keys.issubset(normalized_columns):
        uploaded_file.seek(0)
        frame = pd.read_csv(uploaded_file, header=None, names=SOURCE_COLUMNS)
    else:
        frame = frame.rename(columns={normalized_columns[_column_key(column)]: column for column in SOURCE_COLUMNS})
    return frame


def clean_data(frames: list[pd.DataFrame]) -> tuple[pd.DataFrame, dict[str, int]]:
    """Combine uploaded frames and normalize common student-data issues."""
    combined = pd.concat(frames, ignore_index=True)
    original_rows = len(combined)
    combined = combined[SOURCE_COLUMNS].copy()
    combined["name"] = _clean_text(combined["name"], "Unknown").str.title()
    combined["gender"] = _clean_text(combined["gender"], "Unknown").str.lower().replace(
        {"f": "Female", "female": "Female", "woman": "Female", "girl": "Female", "m": "Male", "male": "Male", "man": "Male", "boy": "Male"}
    )
    combined["gender"] = combined["gender"].where(combined["gender"].isin(["Female", "Male"]), "Unknown")
    combined["grade"] = pd.to_numeric(combined["grade"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    for subject in SUBJECTS:
        combined[subject] = pd.to_numeric(
            combined[subject].astype(str).str.replace("marks", "", case=False, regex=False).str.extract(r"(-?\d+(?:\.\d+)?)")[0],
            errors="coerce",
        )
    valid_rows = combined["grade"].between(1, 12) & combined[SUBJECTS].apply(lambda column: column.between(0, 100)).all(axis=1)
    combined = combined.loc[valid_rows].copy()
    combined["grade"] = combined["grade"].astype(int)
    combined["student_id"] = range(1, len(combined) + 1)
    combined["unique_name"] = combined["name"] + "_" + combined.groupby("name").cumcount().add(1).astype(str)
    combined["total"] = combined[SUBJECTS].sum(axis=1)
    cleaned = combined[EXPECTED_COLUMNS]
    return cleaned, {"uploaded_rows": original_rows, "cleaned_rows": len(cleaned), "removed_rows": original_rows - len(cleaned)}


@st.cache_data
def load_uploaded_data(uploaded_files: list[Any]) -> tuple[pd.DataFrame, dict[str, int]]:
    """Load and clean one or more CSV uploads."""
    if not uploaded_files:
        raise ValueError("Upload at least one CSV file to begin.")
    return clean_data([_read_upload(uploaded_file) for uploaded_file in uploaded_files])


def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate an uploaded dataset and return it unchanged."""
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


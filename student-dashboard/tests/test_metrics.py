import pandas as pd

from data import clean_data
from metrics import failing_any_rate, passing_all_rate, performance_bands, ranked_students, subject_outlier_summary, subject_summary


def sample_data() -> pd.DataFrame:
    return pd.DataFrame({"unique_name": ["A_1", "B_1", "C_1"], "gender": ["Female", "Male", "Unknown"], "grade": [1, 1, 2], "math": [80, 40, 20], "science": [80, 40, 60], "english": [80, 40, 40], "total": [240, 120, 120]})


def test_ranking_uses_min_rank_for_ties():
    ranked = ranked_students(sample_data())
    assert ranked["rank"].tolist() == [1, 2, 2]


def test_pass_and_fail_rates():
    data = sample_data()
    assert passing_all_rate(data) == 2 / 3 * 100
    assert failing_any_rate(data) == 1 / 3 * 100


def test_band_counts():
    bands = performance_bands(sample_data())
    assert bands.loc["math", "Excellent"] == 1
    assert bands.loc["math", "Pass"] == 1
    assert bands.loc["math", "Fail"] == 1


def test_subject_summary_and_outlier_summary():
    data = sample_data()
    summary = subject_summary(data)
    outliers = subject_outlier_summary(data)
    assert summary.iloc[0]["subject"] == "Science"
    assert outliers["outliers"].sum() == 0


def test_clean_data_normalizes_quoted_names_and_gender():
    raw = pd.DataFrame(
        {
            "name": [' "navya" ', "'ROHAN'"],
            "gender": [' "female" ', "'M'"],
            "grade": [1, 2],
            "math": [80, 70],
            "science": [75, 65],
            "english": [90, 60],
            "total": [0, 0],
        }
    )

    cleaned, _ = clean_data([raw])

    assert cleaned["name"].tolist() == ["Navya", "Rohan"]
    assert cleaned["gender"].tolist() == ["Female", "Male"]


def test_clean_data_removes_quotes_inside_text_values():
    raw = pd.DataFrame(
        {
            "name": ["N'a'vya"],
            "gender": ["‘female’"],
            "grade": [1],
            "math": [80],
            "science": [70],
            "english": [90],
            "total": [0],
        }
    )

    cleaned, _ = clean_data([raw])

    assert cleaned.loc[0, "name"] == "Navya"
    assert cleaned.loc[0, "gender"] == "Female"


def test_clean_data_removes_quotes_from_display_names():
    raw = pd.DataFrame(
        {
            "name": ['"Aryan"', "'Diya'", "‘Ananya’"],
            "gender": ["Male", "Female", "Female"],
            "grade": [1, 2, 3],
            "math": [80, 70, 60],
            "science": [70, 60, 50],
            "english": [90, 80, 70],
            "total": [0, 0, 0],
        }
    )

    cleaned, _ = clean_data([raw])

    assert cleaned["name"].tolist() == ["Aryan", "Diya", "Ananya"]
    assert cleaned["unique_name"].tolist() == ["Aryan_1", "Diya_1", "Ananya_1"]

def test_clean_data_maps_numeric_gender_codes():
    raw = pd.DataFrame(
        {
            "name": ["Navya", "Rohan", "Myra"],
            "gender": ["0", "1", " 1 "],
            "grade": [1, 2, 3],
            "math": [80, 70, 60],
            "science": [70, 60, 50],
            "english": [90, 80, 70],
            "total": [0, 0, 0],
        }
    )

    cleaned, _ = clean_data([raw])

    assert cleaned["gender"].tolist() == ["Female", "Male", "Male"]


def test_clean_data_removes_outliers_across_combined_files():
    typical = pd.DataFrame(
        {
            "name": [f"Student {index}" for index in range(30)],
            "gender": ["F", "M"] * 15,
            "grade": [5] * 30,
            "math": [50 + index % 5 for index in range(30)],
            "science": [50 + index % 4 for index in range(30)],
            "english": [50 + index % 3 for index in range(30)],
            "total": [0] * 30,
        }
    )
    extreme = pd.DataFrame({"name": ["'Outlier'"], "gender": ["f"], "grade": ["Grade 5"], "math": ["100 marks"], "science": [100], "english": [100], "total": [300]})

    cleaned, report = clean_data([typical, extreme])

    assert "Outlier" not in cleaned["name"].tolist()
    assert report["outlier_rows"] == 1
    assert report["removed_rows"] == report["invalid_rows"] + report["outlier_rows"]
    assert cleaned["student_id"].tolist() == list(range(1, len(cleaned) + 1))
    assert subject_outlier_summary(cleaned)["outliers"].sum() == 0


def test_small_uploads_keep_every_valid_row():
    raw = pd.DataFrame({"name": ["A", "B", "C"], "gender": ["F", "M", "F"], "grade": [1, 1, 1], "math": [0, 50, 100], "science": [50, 50, 50], "english": [50, 50, 50], "total": [0, 0, 0]})

    _, report = clean_data([raw])

    assert report["outlier_rows"] == 0

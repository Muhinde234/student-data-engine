import pandas as pd

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
    assert summary.iloc[0]["subject"] == "Math"
    assert outliers["outliers"].sum() == 0
"""Pure calculation functions used by the dashboard and tests."""

import pandas as pd


SUBJECTS = ["math", "science", "english"]
BANDS = ["Fail", "Pass", "Good", "Excellent"]


def passing_all_rate(data: pd.DataFrame) -> float:
    """Return the percentage of students passing every subject."""
    return float(data[SUBJECTS].ge(40).all(axis=1).mean() * 100)


def failing_any_rate(data: pd.DataFrame) -> float:
    """Return the percentage of students failing at least one subject."""
    return float(data[SUBJECTS].lt(40).any(axis=1).mean() * 100)


def ranked_students(data: pd.DataFrame) -> pd.DataFrame:
    """Add competition ranks, where tied totals share the minimum rank."""
    ranked = data.copy()
    ranked["rank"] = ranked["total"].rank(method="min", ascending=False).astype(int)
    columns = ["rank", "unique_name", "gender", "grade", *SUBJECTS, "total"]
    return ranked.sort_values(["rank", "unique_name"])[columns]


def performance_bands(data: pd.DataFrame) -> pd.DataFrame:
    """Count Fail, Pass, Good, and Excellent scores for each subject."""
    counts = {}
    for subject in SUBJECTS:
        counts[subject] = pd.cut(data[subject], bins=[-1, 39, 59, 79, 100], labels=BANDS).value_counts().reindex(BANDS, fill_value=0)
    return pd.DataFrame(counts).T


def top_student_per_grade(data: pd.DataFrame) -> pd.DataFrame:
    """Return all top-ranked students for each grade, including ties."""
    ranked = ranked_students(data)
    return ranked[ranked.groupby("grade")["rank"].transform("min") == ranked["rank"]]
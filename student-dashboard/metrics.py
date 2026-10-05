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


def gender_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Compare group size, scores, and pass rates by gender label."""
    summary = data.groupby("gender").agg(
        students=("student_id", "size"),
        average_total=("total", "mean"),
        average_math=("math", "mean"),
        average_science=("science", "mean"),
        average_english=("english", "mean"),
    )
    summary["passing_all"] = data.groupby("gender")[SUBJECTS].apply(lambda group: group.ge(40).all(axis=1).mean() * 100)
    return summary.reset_index().sort_values("average_total", ascending=False)


def subject_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize average scores and pass rates for every subject."""
    rows = []
    for subject in SUBJECTS:
        rows.append(
            {
                "subject": subject.title(),
                "average_score": data[subject].mean(),
                "pass_rate": data[subject].ge(40).mean() * 100,
                "excellent_rate": data[subject].ge(80).mean() * 100,
            }
        )
    return pd.DataFrame(rows).sort_values("average_score", ascending=False)


def grade_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize cohort size, average score, and pass rate by grade."""
    grouped = data.groupby("grade")
    summary = grouped.agg(students=("student_id", "size"), average_total=("total", "mean"))
    summary["passing_all"] = grouped[SUBJECTS].apply(lambda group: group.ge(40).all(axis=1).mean() * 100)
    return summary.reset_index()


def subject_outlier_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Count IQR outliers and report valid score bounds for each subject and the total."""
    rows = []
    for subject in [*SUBJECTS, "total"]:
        scores = data[subject]
        q1 = scores.quantile(0.25)
        q3 = scores.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        rows.append(
            {
                "subject": subject.title(),
                "outliers": int(((scores < lower) | (scores > upper)).sum()),
                "minimum": float(scores.min()),
                "maximum": float(scores.max()),
            }
        )
    return pd.DataFrame(rows)
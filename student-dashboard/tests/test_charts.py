import pandas as pd

from charts import SCORE_LABELS, gender_subject_comparison, score_histogram, subject_outcomes


def test_score_histogram_uses_all_ten_score_ranges():
    data = pd.DataFrame({"math": [0, 9, 10, 49, 50, 99, 100]})

    figure = score_histogram(data, "math")

    assert figure.data[0].x.tolist() == SCORE_LABELS
    assert figure.data[0].y.tolist() == [2, 1, 0, 0, 1, 1, 0, 0, 0, 2]


def test_gender_chart_keeps_legend_visible():
    data = pd.DataFrame({"gender": ["Female", "Male"], "math": [70, 80], "science": [65, 75], "english": [72, 78]})

    figure = gender_subject_comparison(data)

    assert figure.layout.showlegend is True


def test_subject_health_chart_keeps_legend_visible():
    data = pd.DataFrame({"math": [70, 80], "science": [65, 75], "english": [72, 78]})

    figure = subject_outcomes(data)

    assert figure.layout.showlegend is True
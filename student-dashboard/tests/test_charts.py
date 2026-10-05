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

def test_multi_series_charts_reserve_space_between_title_and_plot_for_legend():
    from charts import TITLE_BAND, band_chart, total_by_gender
    from metrics import performance_bands

    data = pd.DataFrame(
        {"gender": ["Female", "Male", "Female", "Male"], "grade": [1, 1, 2, 2], "math": [70, 30, 90, 50], "science": [65, 45, 85, 20], "english": [72, 60, 40, 95]}
    )
    data["total"] = data[["math", "science", "english"]].sum(axis=1)

    for figure in [score_histogram(data, "math"), gender_subject_comparison(data), subject_outcomes(data), total_by_gender(data), band_chart(performance_bands(data))]:
        legend_top_px = (1 - figure.layout.legend.y) * figure.layout.height
        assert figure.layout.showlegend is True
        assert figure.layout.legend.yref == "container"
        assert legend_top_px >= TITLE_BAND
        assert figure.layout.margin.t >= legend_top_px + 30

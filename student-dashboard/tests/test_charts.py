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

def test_charts_keep_legend_above_plot_and_below_toolbar_with_wrapping_titles():
    from charts import TOOLBAR_BAND, average_total_by_grade, band_chart, correlation_heatmap, pass_rate_by_grade, total_by_gender
    from metrics import performance_bands

    data = pd.DataFrame(
        {"gender": ["Female", "Male", "Female", "Male"], "grade": [1, 1, 2, 2], "math": [70, 30, 90, 50], "science": [65, 45, 85, 20], "english": [72, 60, 40, 95]}
    )
    data["total"] = data[["math", "science", "english"]].sum(axis=1)

    legend_charts = [
        score_histogram(data, "math"),
        gender_subject_comparison(data),
        subject_outcomes(data),
        total_by_gender(data),
        band_chart(performance_bands(data)),
        average_total_by_grade(data),
        pass_rate_by_grade(data),
    ]
    for figure in legend_charts:
        legend = figure.layout.legend
        assert figure.layout.showlegend is True
        # Anchored on top of the plot, so plotly pushes the margin as the legend wraps.
        assert (legend.yref, legend.y, legend.yanchor) == ("paper", 1.0, "bottom")
        # The blank legend title row keeps entries clear of the toolbar.
        assert legend.title.side == "top" and legend.title.font.size >= TOOLBAR_BAND - 12

    for figure in [*legend_charts, correlation_heatmap(data)]:
        assert figure.layout.margin.t >= TOOLBAR_BAND
        assert figure.layout.meta["title"] and figure.layout.meta["subtitle"]
        assert not figure.layout.title.text

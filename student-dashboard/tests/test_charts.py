import pandas as pd

from charts import SCORE_LABELS, score_histogram


def test_score_histogram_uses_all_ten_score_ranges():
    data = pd.DataFrame({"math": [0, 9, 10, 49, 50, 99, 100]})

    figure = score_histogram(data, "math")

    assert figure.data[0].x.tolist() == SCORE_LABELS
    assert figure.data[0].y.tolist() == [2, 1, 0, 0, 1, 1, 0, 0, 0, 2]
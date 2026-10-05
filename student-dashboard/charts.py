"""Interactive Plotly charts for the student dashboard.

Every chart title states the finding for the data currently shown, the subtitle says
how to read the chart, and charts with two or more series reserve a band for the legend
between the subtitle and the plot so the legend never overlaps the title or the marks.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go


SUBJECTS = ["math", "science", "english"]
PASS_MARK = 40
EXCELLENT_MARK = 80

# Colours validated for colour-blind separation against the chart surface.
BLUE = "#2A6CB8"
CORAL = "#E2583F"
AMBER = "#D99A2B"
GREEN = "#2E9A5E"
RED = "#C8423C"
GRAY = "#8A8F96"
INK = "#172A3A"
MUTED = "#65727C"
GRID = "#E8E3DB"
AXIS = "#D9D4CC"
SURFACE = "#FBF8F3"
NEUTRAL = "#EFECE6"

# Colour follows the entity, so filtering never repaints the groups that remain.
GENDER_COLORS = {"Female": CORAL, "Male": BLUE, "Unknown": GRAY}
PALETTE = {"Fail": RED, "Pass": AMBER, "Good": GREEN, "Excellent": BLUE}
BAND_TEXT = {"Fail": "#FFFFFF", "Pass": INK, "Good": "#FFFFFF", "Excellent": "#FFFFFF"}

CHART_FONT = "DM Sans, sans-serif"
TITLE_FONT = "Space Grotesk, sans-serif"
SCORE_BINS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
SCORE_LABELS = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-100"]

TITLE_BAND = 76
LEGEND_BAND = 34
REFERENCE_BAND = 84


def polish(figure: go.Figure, title: str, subtitle: str, legend: bool = False, height: int = 430) -> go.Figure:
    """Apply shared styling and reserve fixed space for the title, subtitle, and legend."""
    top = TITLE_BAND + (LEGEND_BAND if legend else 0) + 14
    has_reference = any(annotation.name == "reference" for annotation in figure.layout.annotations)
    figure.update_layout(
        autosize=True,
        height=height,
        margin=dict(l=12, r=REFERENCE_BAND if has_reference else 28, t=top, b=12),
        title=dict(
            text=f"<b>{title}</b>",
            subtitle=dict(text=subtitle, font=dict(family=CHART_FONT, color=MUTED, size=13)),
            font=dict(family=TITLE_FONT, color=INK, size=17),
            x=0,
            xref="paper",
            xanchor="left",
            y=1,
            yref="container",
            yanchor="top",
            pad=dict(t=14),
        ),
        showlegend=legend,
        legend=dict(
            orientation="h",
            x=0,
            xref="paper",
            xanchor="left",
            y=1 - (TITLE_BAND + 2) / height,
            yref="container",
            yanchor="top",
            title=None,
            font=dict(family=CHART_FONT, color=INK, size=12),
            bgcolor="rgba(0,0,0,0)",
            traceorder="normal",
        ),
        font=dict(family=CHART_FONT, color=INK, size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=SURFACE,
        hoverlabel=dict(bgcolor=INK, bordercolor=INK, font=dict(color="#FFFFFF", family=CHART_FONT)),
        bargap=0.22,
    )
    figure.update_xaxes(showgrid=False, linecolor=AXIS, tickfont=dict(color=MUTED), title_font=dict(color=INK, size=12), automargin=True)
    figure.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=AXIS, tickfont=dict(color=MUTED), title_font=dict(color=INK, size=12), automargin=True)
    return figure


def _reference_line(figure: go.Figure, y: float, label: str, value: str) -> None:
    """Draw a horizontal reference line labelled in the right margin, clear of the data."""
    figure.add_hline(y=y, line=dict(color=MUTED, width=1))
    figure.add_annotation(
        name="reference",
        x=1,
        xref="paper",
        y=y,
        text=f"{label}<br><b>{value}</b>",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        xshift=6,
        align="left",
        font=dict(color=MUTED, size=11),
    )


def _label(subject: str) -> str:
    return subject.title()


def _passing_all(data: pd.DataFrame) -> pd.Series:
    return data[SUBJECTS].ge(PASS_MARK).all(axis=1)


def score_histogram(data: pd.DataFrame, subject: str) -> go.Figure:
    """Show student counts across ten-mark ranges, split at the pass mark."""
    ranges = pd.cut(data[subject], bins=SCORE_BINS, labels=SCORE_LABELS, include_lowest=True, right=False)
    counts = ranges.value_counts().reindex(SCORE_LABELS, fill_value=0)
    below_share = data[subject].lt(PASS_MARK).mean() * 100
    colors = [RED if int(label.split("-")[0]) < PASS_MARK else BLUE for label in SCORE_LABELS]
    figure = go.Figure(
        go.Bar(
            x=counts.index.astype(str).to_numpy(),
            y=counts.to_numpy(),
            text=counts.to_numpy(),
            textposition="outside",
            textfont=dict(color=INK, size=11),
            cliponaxis=False,
            marker=dict(color=colors, cornerradius=4),
            showlegend=False,
            hovertemplate="Marks %{x}<br>%{y} students<extra></extra>",
        )
    )
    # Legend-only entries explain the two bar colours without splitting the data trace.
    for name, color in [(f"Below pass mark (0-{PASS_MARK - 1})", RED), (f"Pass mark or above ({PASS_MARK}-100)", BLUE)]:
        figure.add_trace(go.Bar(x=[None], y=[None], name=name, marker=dict(color=color), hoverinfo="skip"))
    # The legend names the split, so the divider needs no label of its own to collide with bar counts.
    figure.add_vline(x=3.5, line=dict(color=INK, width=1.5))
    figure.update_layout(
        barmode="overlay",
        xaxis_title=f"{_label(subject)} mark range",
        yaxis=dict(title="Number of students", range=[0, max(counts.max(), 1) * 1.15]),
    )
    return polish(
        figure,
        f"{_label(subject)}: {below_share:.0f}% of students score below the pass mark",
        f"Students in each ten-mark range · divider at the pass mark of {PASS_MARK} · average {data[subject].mean():.1f} / 100",
        legend=True,
    )


def average_total_by_grade(data: pd.DataFrame) -> go.Figure:
    """Show how the average total changes across grades against the cohort average."""
    averages = data.groupby("grade", as_index=False)["total"].mean()
    best = averages.loc[averages["total"].idxmax()]
    cohort_average = data["total"].mean()
    figure = go.Figure(
        go.Scatter(
            x=averages["grade"],
            y=averages["total"],
            mode="lines+markers",
            line=dict(color=BLUE, width=2.5),
            marker=dict(size=9, color=BLUE, line=dict(color=SURFACE, width=2)),
            hovertemplate="Grade %{x}<br>Average total: %{y:.1f} / 300<extra></extra>",
        )
    )
    _reference_line(figure, cohort_average, "Cohort avg", f"{cohort_average:.1f}")
    figure.add_annotation(x=best["grade"], y=best["total"], text=f"<b>{best['total']:.1f}</b>", showarrow=False, yanchor="bottom", yshift=10, font=dict(color=INK, size=12))
    figure.update_layout(xaxis=dict(title="Grade", dtick=1), yaxis_title="Average total (out of 300)")
    if len(averages) > 1:
        title = f"Grade {int(best['grade'])} has the highest average total ({best['total']:.1f} / 300)"
    else:
        title = f"Grade {int(best['grade'])} averages {best['total']:.1f} out of 300"
    return polish(figure, title, "Mean Math + Science + English score per grade, compared with the cohort average")


def pass_rate_by_grade(data: pd.DataFrame) -> go.Figure:
    """Show the share of students passing all three subjects in each grade."""
    rates = _passing_all(data).groupby(data["grade"]).mean().mul(100).reset_index(name="rate")
    best = rates.loc[rates["rate"].idxmax()]
    cohort_rate = _passing_all(data).mean() * 100
    figure = go.Figure(
        go.Bar(
            x=rates["grade"],
            y=rates["rate"],
            text=[f"{value:.0f}%" for value in rates["rate"]],
            textposition="outside",
            textfont=dict(color=INK, size=11),
            cliponaxis=False,
            marker=dict(color=BLUE, cornerradius=4),
            hovertemplate="Grade %{x}<br>%{y:.1f}% pass all three subjects<extra></extra>",
        )
    )
    _reference_line(figure, cohort_rate, "Cohort", f"{cohort_rate:.0f}%")
    upper = min(100, max(rates["rate"].max(), cohort_rate) * 1.25 + 5)
    figure.update_layout(xaxis=dict(title="Grade", dtick=1), yaxis=dict(title="Students passing all 3 subjects", ticksuffix="%", range=[0, upper]))
    if len(rates) > 1:
        title = f"Grade {int(best['grade'])} has the most students passing all three subjects ({best['rate']:.0f}%)"
    else:
        title = f"{best['rate']:.0f}% of Grade {int(best['grade'])} pass all three subjects"
    return polish(figure, title, f"Share of students scoring at least {PASS_MARK} in Math, Science, and English")


def total_by_gender(data: pd.DataFrame) -> go.Figure:
    """Compare total score distributions across gender labels."""
    figure = go.Figure()
    medians = {}
    for gender, color in GENDER_COLORS.items():
        group = data.loc[data["gender"] == gender, "total"]
        if group.empty:
            continue
        medians[gender] = group.median()
        figure.add_trace(
            go.Box(
                y=group,
                name=gender,
                marker=dict(color=color),
                line=dict(color=color, width=2),
                # Subgroup IQR fences differ from the cohort's, so per-group dots would
                # reappear as "outliers" even after cleaning removed the cohort outliers.
                boxpoints=False,
                boxmean=True,
                hoverinfo="y+name",
            )
        )
    figure.update_layout(xaxis_title="Gender", yaxis_title="Total score (out of 300)")
    ranked = sorted(medians.items(), key=lambda item: item[1], reverse=True)
    if len(ranked) >= 2:
        title = f"{ranked[0][0]} students have the higher median total ({ranked[0][1]:.0f} vs {ranked[1][1]:.0f})"
    else:
        title = f"Median total for {ranked[0][0].lower()} students: {ranked[0][1]:.0f} / 300"
    return polish(figure, title, "Box shows the middle 50% of students · line is the median, dashed line the mean", legend=True)


def band_chart(bands: pd.DataFrame) -> go.Figure:
    """Show each subject's share of Fail, Pass, Good, and Excellent scores."""
    totals = bands.sum(axis=1).replace(0, 1)
    shares = bands.div(totals, axis=0).mul(100)
    labels = [_label(subject) for subject in shares.index]
    figure = go.Figure()
    for band, color in PALETTE.items():
        values = shares[band]
        figure.add_trace(
            go.Bar(
                y=labels,
                x=values,
                name=band,
                orientation="h",
                marker=dict(color=color, line=dict(color=SURFACE, width=2)),
                text=[f"{value:.0f}%" if value >= 6 else "" for value in values],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color=BAND_TEXT[band], size=12),
                customdata=bands[band],
                hovertemplate=f"%{{y}} · {band}<br>%{{customdata}} students (%{{x:.1f}}%)<extra></extra>",
            )
        )
    figure.update_layout(
        barmode="stack",
        xaxis=dict(title="Share of students", ticksuffix="%", range=[0, 100]),
        yaxis=dict(autorange="reversed"),
    )
    worst = shares["Fail"].idxmax()
    return polish(
        figure,
        f"{_label(worst)} has the largest share of failing scores ({shares.loc[worst, 'Fail']:.0f}%)",
        f"Fail below {PASS_MARK} · Pass {PASS_MARK}-59 · Good 60-79 · Excellent {EXCELLENT_MARK}+",
        legend=True,
        height=380,
    )


def correlation_heatmap(data: pd.DataFrame) -> go.Figure:
    """Show how strongly subject scores move together."""
    correlation = data[SUBJECTS].corr().fillna(0)
    labels = [_label(subject) for subject in SUBJECTS]
    # A subject always correlates 1.00 with itself; blanking the diagonal keeps focus on the pairs.
    cells = correlation.to_numpy(copy=True)
    np.fill_diagonal(cells, np.nan)
    figure = go.Figure(
        go.Heatmap(
            z=cells,
            x=labels,
            y=labels,
            zmin=-1,
            zmax=1,
            colorscale=[[0, CORAL], [0.5, NEUTRAL], [1, BLUE]],
            texttemplate="%{z:.2f}",
            textfont=dict(color=INK, size=14),
            xgap=2,
            ygap=2,
            colorbar=dict(title=dict(text="r", font=dict(color=INK)), tickvals=[-1, -0.5, 0, 0.5, 1], tickfont=dict(color=MUTED), thickness=12),
            hovertemplate="%{y} vs %{x}<br>Correlation r = %{z:.2f}<extra></extra>",
        )
    )
    figure.update_yaxes(autorange="reversed", showgrid=False)
    pairs = [(SUBJECTS[i], SUBJECTS[j], correlation.iloc[i, j]) for i in range(3) for j in range(i + 1, 3)]
    first, second, strongest = max(pairs, key=lambda pair: abs(pair[2]))
    if abs(strongest) < 0.2:
        title = "Subject scores are largely independent of each other"
    else:
        direction = "rise together" if strongest > 0 else "move in opposite directions"
        title = f"{_label(first)} and {_label(second)} scores {direction} (r = {strongest:.2f})"
    return polish(figure, title, "Correlation from -1 (opposite) through 0 (no link) to +1 (move together)", height=420)


def gender_subject_comparison(data: pd.DataFrame) -> go.Figure:
    """Compare average subject scores for each gender label."""
    averages = data.groupby("gender")[SUBJECTS].mean()
    labels = [_label(subject) for subject in SUBJECTS]
    figure = go.Figure()
    for gender, color in GENDER_COLORS.items():
        if gender not in averages.index:
            continue
        values = averages.loc[gender]
        figure.add_trace(
            go.Bar(
                x=labels,
                y=values.values,
                name=gender,
                marker=dict(color=color, cornerradius=4, line=dict(color=SURFACE, width=2)),
                text=[f"{value:.1f}" for value in values],
                textposition="outside",
                textfont=dict(color=INK, size=11),
                cliponaxis=False,
                hovertemplate=f"{gender} · %{{x}}<br>Average %{{y:.1f}} / 100<extra></extra>",
            )
        )
    _reference_line(figure, PASS_MARK, "Pass mark", f"{PASS_MARK}")
    figure.update_layout(barmode="group", yaxis=dict(title="Average score (out of 100)", range=[0, 100]))
    known = averages.loc[averages.index.isin(["Female", "Male"])]
    if len(known) == 2:
        gaps = (known.loc["Female"] - known.loc["Male"])
        subject = gaps.abs().idxmax()
        leader = "Female" if gaps[subject] > 0 else "Male"
        title = f"Largest gender gap is in {_label(subject)}: {leader} students lead by {abs(gaps[subject]):.1f} points"
    else:
        title = "Average subject scores for the selected students"
    return polish(figure, title, "Observed averages in this dataset only; differences do not explain causes", legend=True)


def subject_outcomes(data: pd.DataFrame) -> go.Figure:
    """Compare pass and excellence rates for each subject on one percentage axis."""
    labels = [_label(subject) for subject in SUBJECTS]
    pass_rates = data[SUBJECTS].ge(PASS_MARK).mean().mul(100)
    excellent_rates = data[SUBJECTS].ge(EXCELLENT_MARK).mean().mul(100)
    figure = go.Figure()
    for name, values, color in [(f"Pass rate ({PASS_MARK}+)", pass_rates, BLUE), (f"Excellent rate ({EXCELLENT_MARK}+)", excellent_rates, AMBER)]:
        figure.add_trace(
            go.Bar(
                x=labels,
                y=values.values,
                name=name,
                marker=dict(color=color, cornerradius=4, line=dict(color=SURFACE, width=2)),
                text=[f"{value:.0f}%" for value in values],
                textposition="outside",
                textfont=dict(color=INK, size=11),
                cliponaxis=False,
                hovertemplate=f"%{{x}} · {name}<br>%{{y:.1f}}% of students<extra></extra>",
            )
        )
    figure.update_layout(barmode="group", yaxis=dict(title="Share of students", ticksuffix="%", range=[0, 100]))
    best = pass_rates.idxmax()
    worst = pass_rates.idxmin()
    return polish(
        figure,
        f"{_label(best)} has the highest pass rate ({pass_rates[best]:.0f}%); {_label(worst)} the lowest ({pass_rates[worst]:.0f}%)",
        "Share of students reaching the pass mark and the excellent mark in each subject",
        legend=True,
    )

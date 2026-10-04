"""Interactive Plotly charts for the student dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PALETTE = {"Fail": "#C94C4C", "Pass": "#E0A458", "Good": "#4C956C", "Excellent": "#2F6690"}
CHART_FONT = "DM Sans, sans-serif"


def polish(figure: go.Figure) -> go.Figure:
    """Apply the dashboard's shared chart styling."""
    figure.update_layout(
        autosize=True,
        height=390,
        margin=dict(l=18, r=18, t=58, b=24),
        font=dict(family=CHART_FONT, color="#263238", size=12),
        title_font=dict(family="Space Grotesk, sans-serif", color="#172A3A", size=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FBF8F3",
        showlegend=False,
        hoverlabel=dict(bgcolor="#172A3A", font=dict(color="#FFFFFF", family=CHART_FONT)),
    )
    figure.update_xaxes(showgrid=False, linecolor="#D9D4CC", tickfont=dict(color="#263238"), title_font=dict(color="#172A3A"))
    figure.update_yaxes(gridcolor="#E8E3DB", zeroline=False, tickfont=dict(color="#263238"), title_font=dict(color="#172A3A"))
    return figure


def score_histogram(data: pd.DataFrame, subject: str) -> go.Figure:
    """Show student counts across clearly named ten-mark ranges."""
    bins = list(range(0, 91, 10)) + [101]
    labels = [f"{start}-{start + 9}" for start in range(0, 90, 10)] + ["90-100"]
    ranges = pd.cut(data[subject], bins=bins, labels=labels, include_lowest=True, right=False)
    counts = ranges.value_counts().reindex(labels, fill_value=0).rename_axis("mark_range").reset_index(name="students")
    figure = px.bar(counts, x="mark_range", y="students", text="students", color_discrete_sequence=["#2F6690"])
    average = data[subject].mean()
    figure.update_layout(
        title=dict(text=f"How {subject.title()} marks are spread", subtitle=dict(text="Each bar shows the number of students in a ten-mark range")),
        xaxis_title="Mark range",
        yaxis_title="Number of students",
    )
    figure.update_traces(textposition="outside", hovertemplate="Mark range: %{x}<br>Students: %{y}<extra></extra>")
    figure.add_annotation(x=0.98, y=1.08, xref="paper", yref="paper", text=f"Average mark: {average:.1f}", showarrow=False, font=dict(color="#E56B56", size=12))
    return polish(figure)


def average_total_by_grade(data: pd.DataFrame) -> go.Figure:
    """Show how average total changes across grades."""
    averages = data.groupby("grade", as_index=False)["total"].mean()
    figure = px.line(averages, x="grade", y="total", markers=True, color_discrete_sequence=["#2F6690"])
    figure.update_layout(title=dict(text="Average total by grade", subtitle=dict(text="Mean combined score for each grade")))
    figure.update_traces(line=dict(width=3), marker=dict(size=8))
    return polish(figure)


def total_by_gender(data: pd.DataFrame) -> go.Figure:
    """Compare total score distributions across gender labels."""
    figure = px.box(data, x="gender", y="total", color="gender", color_discrete_sequence=["#2F6690", "#4C956C", "#E0A458"])
    figure.update_layout(title=dict(text="Total score spread by gender", subtitle=dict(text="Median and score range for each group")))
    return polish(figure)


def band_chart(bands: pd.DataFrame) -> go.Figure:
    """Show subject performance bands as a stacked bar chart."""
    long = bands.reset_index(names="subject").melt(id_vars="subject", var_name="band", value_name="students")
    figure = px.bar(long, x="subject", y="students", color="band", barmode="stack", color_discrete_map=PALETTE)
    figure.update_layout(title=dict(text="Performance bands by subject", subtitle=dict(text="Students grouped by score level")))
    figure.update_layout(showlegend=True, legend=dict(orientation="h", y=1.08, x=0))
    return polish(figure)


def correlation_heatmap(data: pd.DataFrame) -> go.Figure:
    """Show correlations between subject scores."""
    correlation = data[["math", "science", "english"]].corr()
    figure = px.imshow(correlation, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="Blues")
    figure.update_layout(title=dict(text="Subject score relationships", subtitle=dict(text="Correlation between Math, Science, and English")))
    return polish(figure)


def gender_subject_comparison(data: pd.DataFrame) -> go.Figure:
    """Compare average subject scores for each gender label."""
    averages = data.groupby("gender")[["math", "science", "english"]].mean().reset_index()
    long = averages.melt(id_vars="gender", var_name="subject", value_name="average_score")
    figure = px.bar(
        long,
        x="subject",
        y="average_score",
        color="gender",
        barmode="group",
        color_discrete_sequence=["#E56B56", "#2F6690", "#E0A458"],
    )
    figure.update_layout(
        title=dict(text="Average subject scores by gender", subtitle=dict(text="Observed mean scores for each group")),
        yaxis_title="Average score",
        showlegend=True,
        legend=dict(orientation="h", y=1.08, x=0, title=None),
    )
    return polish(figure)


def subject_outcomes(data: pd.DataFrame) -> go.Figure:
    """Compare average score and pass rate for each subject."""
    outcomes = data[["math", "science", "english"]].agg(["mean", lambda values: values.ge(40).mean() * 100]).T.reset_index()
    outcomes.columns = ["subject", "average_score", "pass_rate"]
    long = outcomes.melt(id_vars="subject", var_name="measure", value_name="value")
    long["measure"] = long["measure"].replace({"average_score": "Average score", "pass_rate": "Pass rate"})
    figure = px.bar(long, x="subject", y="value", color="measure", barmode="group", color_discrete_sequence=["#2F6690", "#E56B56"])
    figure.update_layout(title=dict(text="Subject health: score and pass rate", subtitle=dict(text="Average mark compared with the 40-point pass threshold")), yaxis_title="Percent / score")
    return polish(figure)
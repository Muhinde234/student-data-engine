"""Interactive Plotly charts for the student dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PALETTE = {"Fail": "#C94C4C", "Pass": "#E0A458", "Good": "#4C956C", "Excellent": "#2F6690"}


def score_histogram(data: pd.DataFrame, subject: str) -> go.Figure:
    """Show the selected subject's score distribution."""
    figure = px.histogram(data, x=subject, nbins=20, color_discrete_sequence=["#2F6690"])
    figure.update_layout(title=f"Most {subject.title()} scores cluster in this range")
    return figure


def average_total_by_grade(data: pd.DataFrame) -> go.Figure:
    """Show how average total changes across grades."""
    averages = data.groupby("grade", as_index=False)["total"].mean()
    figure = px.line(averages, x="grade", y="total", markers=True, color_discrete_sequence=["#2F6690"])
    figure.update_layout(title="Average total changes across grades")
    return figure


def total_by_gender(data: pd.DataFrame) -> go.Figure:
    """Compare total score distributions across gender labels."""
    figure = px.box(data, x="gender", y="total", color="gender", color_discrete_sequence=["#2F6690", "#4C956C", "#E0A458"])
    figure.update_layout(title="Total score spread differs across gender groups")
    return figure


def band_chart(bands: pd.DataFrame) -> go.Figure:
    """Show subject performance bands as a stacked bar chart."""
    long = bands.reset_index(names="subject").melt(id_vars="subject", var_name="band", value_name="students")
    figure = px.bar(long, x="subject", y="students", color="band", barmode="stack", color_discrete_map=PALETTE)
    figure.update_layout(title="Pass and higher performance make up these subject totals")
    return figure


def correlation_heatmap(data: pd.DataFrame) -> go.Figure:
    """Show correlations between subject scores."""
    correlation = data[["math", "science", "english"]].corr()
    figure = px.imshow(correlation, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="Blues")
    figure.update_layout(title="Subject scores have these relationships")
    return figure
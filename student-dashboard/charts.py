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
        margin=dict(l=12, r=12, t=24, b=12),
        font=dict(family=CHART_FONT, color="#263238", size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FBF8F3",
        showlegend=False,
        hoverlabel=dict(bgcolor="#172A3A", font=dict(color="#FFFFFF", family=CHART_FONT)),
    )
    figure.update_xaxes(showgrid=False, linecolor="#D9D4CC", tickfont=dict(color="#65727C"))
    figure.update_yaxes(gridcolor="#E8E3DB", zeroline=False, tickfont=dict(color="#65727C"))
    return figure


def score_histogram(data: pd.DataFrame, subject: str) -> go.Figure:
    """Show the selected subject's score distribution."""
    figure = px.histogram(data, x=subject, nbins=20, color_discrete_sequence=["#2F6690"])
    figure.update_layout(title=f"Most {subject.title()} scores cluster in this range")
    return polish(figure)


def average_total_by_grade(data: pd.DataFrame) -> go.Figure:
    """Show how average total changes across grades."""
    averages = data.groupby("grade", as_index=False)["total"].mean()
    figure = px.line(averages, x="grade", y="total", markers=True, color_discrete_sequence=["#2F6690"])
    figure.update_layout(title="Average total changes across grades")
    figure.update_traces(line=dict(width=3), marker=dict(size=8))
    return polish(figure)


def total_by_gender(data: pd.DataFrame) -> go.Figure:
    """Compare total score distributions across gender labels."""
    figure = px.box(data, x="gender", y="total", color="gender", color_discrete_sequence=["#2F6690", "#4C956C", "#E0A458"])
    figure.update_layout(title="Total score spread differs across gender groups")
    return polish(figure)


def band_chart(bands: pd.DataFrame) -> go.Figure:
    """Show subject performance bands as a stacked bar chart."""
    long = bands.reset_index(names="subject").melt(id_vars="subject", var_name="band", value_name="students")
    figure = px.bar(long, x="subject", y="students", color="band", barmode="stack", color_discrete_map=PALETTE)
    figure.update_layout(title="Pass and higher performance make up these subject totals")
    figure.update_layout(showlegend=True, legend=dict(orientation="h", y=1.08, x=0))
    return polish(figure)


def correlation_heatmap(data: pd.DataFrame) -> go.Figure:
    """Show correlations between subject scores."""
    correlation = data[["math", "science", "english"]].corr()
    figure = px.imshow(correlation, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="Blues")
    figure.update_layout(title="Subject scores have these relationships")
    return polish(figure)
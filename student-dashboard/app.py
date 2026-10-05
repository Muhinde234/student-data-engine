import csv
import html
import re

import streamlit as st

from charts import average_total_by_grade, band_chart, correlation_heatmap, gender_subject_comparison, pass_rate_by_grade, score_histogram, subject_outcomes, total_by_gender
from data import SUBJECTS, load_uploaded_data, validate_data
from metrics import failing_any_rate, gender_summary, passing_all_rate, performance_bands, ranked_students, subject_outlier_summary, subject_summary, top_student_per_grade


CHART_TOOLS = [["zoomIn2d", "zoomOut2d", "pan2d", "resetScale2d", "toImage"]]


def show_chart(chart_function, data, *arguments):
    """Render a chart with a wrapping heading and an always-visible zoom / download toolbar.

    Errors are caught so one unusual filtered subset cannot blank the whole dashboard.
    """
    try:
        figure = chart_function(data, *arguments)
    except (KeyError, TypeError, ValueError) as error:
        st.warning(f"This chart needs more data for the current filters: {error}")
        return
    meta = figure.layout.meta or {}
    title = meta.get("title", "")
    st.markdown(
        f'<div class="chart-heading"><div class="chart-title">{html.escape(title)}</div>'
        f'<div class="chart-subtitle">{html.escape(meta.get("subtitle", ""))}</div></div>',
        unsafe_allow_html=True,
    )
    file_name = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "student-chart"
    st.plotly_chart(
        figure,
        width="stretch",
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtons": CHART_TOOLS,
            # Wheel zoom would hijack page scrolling, so zooming goes through the toolbar.
            "scrollZoom": False,
            "responsive": True,
            "toImageButtonOptions": {"format": "png", "filename": file_name, "scale": 2},
        },
    )


def reset_filter_state():
    """Reset both visible filter controls and the applied analysis state."""
    st.session_state.grades_filter = []
    st.session_state.gender_filter = []
    st.session_state.subject_filter = "All subjects"
    st.session_state.applied_grades = []
    st.session_state.applied_genders = []
    st.session_state.applied_subject = "All subjects"


st.set_page_config(page_title="Student Performance Dashboard", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --paper: #f4f0ea;
        --surface: #fbf8f3;
        --ink: #172a3a;
        --muted: #65727c;
        --line: #ddd7ce;
        --coral: #e56b56;
        --blue: #2f6690;
    }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(244, 240, 234, 0.88); }
    [data-testid="stAppViewContainer"] > .main { background: var(--paper); }
    .block-container { max-width: 1440px; padding: 3.5rem 4rem 4rem; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; color: var(--ink) !important; }
    h1 { font-size: clamp(2.5rem, 4vw, 4.6rem); letter-spacing: -0.04em; line-height: 0.98; margin-bottom: 0.65rem; }
    h2 { font-size: 1.4rem; letter-spacing: -0.02em; }
    h3 { font-size: 1rem; letter-spacing: 0; }
    [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] .stCaption, [data-testid="stAppViewContainer"] .stMarkdown { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] *, [data-testid="stAppViewContainer"] [data-testid="stText"] { color: var(--ink) !important; }
    [data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3, [data-testid="stAppViewContainer"] h4 { color: var(--ink) !important; }
    [data-testid="stAppViewContainer"] [data-testid="stTabs"] button p { color: var(--muted) !important; }
    [data-testid="stAppViewContainer"] [data-testid="stTabs"] button[aria-selected="true"] p { color: var(--coral) !important; }
    .hero-kicker { color: var(--coral); font: 700 0.75rem 'DM Sans', sans-serif; letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 0.85rem; }
    .hero-copy { color: var(--muted); font-size: 1.05rem; margin-bottom: 2.25rem; max-width: 620px; }
    .hero-rule { border-top: 1px solid var(--line); margin: 0 0 1.4rem; }
    [data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-radius: 5px; padding: 1.2rem 1.3rem; box-shadow: 0 5px 18px rgba(23, 42, 58, 0.04); }
    [data-testid="stMetricLabel"] { color: var(--muted); font: 600 0.72rem 'DM Sans', sans-serif; text-transform: uppercase; letter-spacing: 0.08em; }
    [data-testid="stMetricValue"] { font-size: 2rem; margin-top: 0.35rem; }
    [data-testid="stTabs"] [role="tablist"] { gap: 1.5rem; border-bottom: 1px solid var(--line); }
    [data-testid="stTabs"] button { color: var(--muted); font: 600 0.86rem 'DM Sans', sans-serif; padding: 0.75rem 0.15rem; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: var(--ink); }
    [data-testid="stTabs"] button[aria-selected="true"] p { color: var(--coral) !important; }
    [data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] * { color: var(--ink) !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: var(--ink) !important; }
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small { color: var(--muted) !important; }
    [data-testid="stSidebar"] .sidebar-brand { color: var(--ink) !important; font: 700 1.45rem 'Space Grotesk', sans-serif; letter-spacing: -0.04em; line-height: 0.9; }
    [data-testid="stSidebar"] .sidebar-brand span { color: var(--coral) !important; }
    [data-testid="stSidebar"] .sidebar-step { color: #e56b56 !important; font: 700 0.68rem 'DM Sans', sans-serif; letter-spacing: 0.12em; text-transform: uppercase; margin: 1.4rem 0 0.45rem; }
    [data-testid="stSidebar"] .sidebar-status { background: #f4f0ea; border: 1px solid var(--line); border-radius: 4px; padding: 0.8rem 0.9rem; margin: 0.8rem 0 1rem; }
    [data-testid="stSidebar"] .sidebar-status strong { display: block; color: var(--ink) !important; font: 600 0.9rem 'DM Sans', sans-serif; }
    [data-testid="stSidebar"] .sidebar-status small { color: var(--muted) !important; font: 400 0.75rem 'DM Sans', sans-serif; }
    [data-testid="stSidebar"] .stButton button, [data-testid="stSidebar"] .stDownloadButton button { width: 100%; background: transparent; color: var(--ink) !important; border: 1px solid var(--line); }
    [data-testid="stSidebar"] .stButton button *, [data-testid="stSidebar"] .stDownloadButton button * { color: var(--ink) !important; }
    [data-testid="stSidebar"] .stButton button:hover, [data-testid="stSidebar"] .stDownloadButton button:hover { border-color: var(--coral); color: var(--ink) !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label, [data-testid="stSidebar"] [data-testid="stMultiSelect"] label { color: #f4f0ea; font-weight: 600; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div { background: var(--paper); border-color: var(--line); }
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] span { background: #e56b56; border: 0; color: #fffaf5 !important; }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); }
    [data-testid="stFileUploader"] label { color: var(--ink) !important; font-weight: 700 !important; }
    [data-testid="stFileUploader"] section { background: #f4f0ea; border: 1px dashed #9aa6ad; border-radius: 4px; }
    [data-testid="stFileUploader"] section > div { color: var(--ink) !important; }
    [data-testid="stFileUploader"] button { background: var(--coral) !important; border-color: var(--coral) !important; color: #fffaf5 !important; }
    [data-testid="stFileUploader"] button p, [data-testid="stFileUploader"] button span { color: #fffaf5 !important; }
    [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] { color: var(--muted) !important; }
    .js-plotly-plot .plotly .modebar { opacity: 1 !important; visibility: visible !important; }
    .js-plotly-plot .plotly .modebar-group { background: rgba(251, 248, 243, 0.92); border-radius: 4px; }
    .js-plotly-plot .plotly .modebar-btn path { fill: #172a3a !important; }
    .js-plotly-plot .plotly .modebar { top: 2px !important; right: 2px !important; }
    .js-plotly-plot .plotly .modebar-group { padding: 2px !important; border: 1px solid var(--line); box-shadow: 0 2px 8px rgba(23, 42, 58, 0.06); }
    .js-plotly-plot .plotly .modebar-btn { padding: 4px 5px !important; }
    .js-plotly-plot .plotly .modebar-btn:hover path, .js-plotly-plot .plotly .modebar-btn.active path { fill: var(--coral) !important; }
    .chart-heading { margin: 1.2rem 0 0.15rem; }
    .chart-title { font: 700 1.05rem/1.3 'Space Grotesk', sans-serif; letter-spacing: -0.01em; }
    .chart-subtitle { font: 400 0.82rem/1.45 'DM Sans', sans-serif; margin-top: 0.2rem; }
    [data-testid="stAppViewContainer"] .chart-title { color: var(--ink) !important; }
    [data-testid="stAppViewContainer"] .chart-subtitle { color: var(--muted) !important; }
    [data-testid="stPlotlyChart"] { min-width: 0; }
    @media (max-width: 1024px) {
        .block-container { padding: 2.5rem 2rem 3rem; }
    }
    @media (max-width: 640px) {
        .block-container { padding: 1.75rem 1rem 2.5rem; }
        .hero-copy { font-size: 0.95rem; margin-bottom: 1.4rem; }
        .control-state { text-align: left; }
        [data-testid="stMetric"] { padding: 0.9rem 1rem; }
        [data-testid="stMetricValue"] { font-size: 1.55rem; }
        [data-testid="stTabs"] [role="tablist"] { gap: 0.9rem; overflow-x: auto; scrollbar-width: none; }
        [data-testid="stTabs"] button { white-space: nowrap; }
        .chart-title { font-size: 0.98rem; }
        .chart-subtitle { font-size: 0.78rem; }
        .data-table table { font-size: 0.76rem; }
        .data-table th, .data-table td { padding: 0.5rem 0.55rem; }
        /* Larger touch targets for the chart toolbar on phones. */
        .js-plotly-plot .plotly .modebar-btn { padding: 6px 7px !important; }
    }
    [data-testid="stForm"] { background: var(--surface); border: 0; padding: 0.15rem 0 0; }
    [data-testid="stForm"] label { color: var(--ink); font: 600 0.75rem 'DM Sans', sans-serif; letter-spacing: 0.03em; }
    [data-testid="stFormSubmitButton"] button { min-height: 2.7rem; border-radius: 4px; font: 700 0.78rem 'DM Sans', sans-serif; letter-spacing: 0.01em; transition: all 150ms ease; }
    [data-testid="stFormSubmitButton"] button[kind="primary"] { background: var(--coral); border-color: var(--coral); color: #fffaf5; }
    [data-testid="stFormSubmitButton"] button[kind="primary"]:hover { background: #c95442; border-color: #c95442; }
    [data-testid="stFormSubmitButton"] button:not([kind="primary"]) { background: transparent; border-color: var(--line); color: var(--muted); }
    [data-testid="stFormSubmitButton"] button:not([kind="primary"]):hover { border-color: var(--ink); color: var(--ink); }
    [data-testid="stFormSubmitButton"] { margin-top: 0; }
    [data-testid="stFormSubmitButton"] button[kind="primary"] *, [data-testid="stFormSubmitButton"] button[kind="primary"] p { color: #fffaf5 !important; }
    .control-actions { border-top: 1px solid var(--line); margin-top: 0.8rem; padding-top: 0.85rem; }
    .control-hint { color: var(--muted); font: 400 0.76rem 'DM Sans', sans-serif; padding-top: 0.55rem; }
    .control-heading { color: var(--ink); font: 700 1.05rem 'Space Grotesk', sans-serif; margin-bottom: 0.1rem; }
    .control-caption { color: var(--muted); font: 400 0.8rem 'DM Sans', sans-serif; }
    .control-state { color: var(--blue); font: 700 0.7rem 'DM Sans', sans-serif; letter-spacing: 0.08em; text-transform: uppercase; text-align: right; padding-top: 0.35rem; }
    .data-table { overflow-x: auto; border: 1px solid var(--line); border-radius: 4px; background: var(--surface); }
    .data-table table { width: 100%; border-collapse: collapse; color: var(--ink); font: 0.82rem 'DM Sans', sans-serif; }
    .data-table th, .data-table th * { background: #172a3a; color: #fffaf5 !important; font-weight: 700; letter-spacing: 0.03em; text-align: left; padding: 0.7rem 0.8rem; }
    .data-table td { color: var(--ink); border-top: 1px solid var(--line); padding: 0.65rem 0.8rem; }
    .data-table tr:nth-child(even) td { background: #f4f0ea; }
    .section-label { color: var(--coral); font: 700 0.7rem 'DM Sans', sans-serif; letter-spacing: 0.13em; text-transform: uppercase; margin: 1.7rem 0 0.35rem; }
    .insight { background: var(--ink); border-left: 4px solid var(--coral); color: #f4f0ea; padding: 1rem 1.2rem; border-radius: 3px; font: 500 0.9rem 'DM Sans', sans-serif; }
    .insight, .insight * { color: #f4f0ea !important; }
    [data-testid="stAppViewContainer"] * { color: var(--ink) !important; }
    [data-testid="stAppViewContainer"] .insight, [data-testid="stAppViewContainer"] .insight * { color: #f4f0ea !important; }
    [data-testid="stAppViewContainer"] [data-testid="stFileUploader"] button, [data-testid="stAppViewContainer"] [data-testid="stFileUploader"] button * { color: #fffaf5 !important; }
    [data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button[kind="primary"], [data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button[kind="primary"] * { color: #fffaf5 !important; }
    [data-testid="stAppViewContainer"] [data-testid="stTabs"] button[aria-selected="true"], [data-testid="stAppViewContainer"] [data-testid="stTabs"] button[aria-selected="true"] p { color: var(--coral) !important; }
    [data-testid="stAppViewContainer"] .data-table th, [data-testid="stAppViewContainer"] .data-table th * { color: #fffaf5 !important; }
    </style>
    <div class="hero-kicker">Student results</div>
    <h1>Student performance report</h1>
    <div class="hero-copy">Review exam results by grade, subject, gender, and student.</div>
    <div class="hero-rule"></div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="sidebar-brand">STUDENT PERFORMANCE <br><span>PLATFORM</span></div>', unsafe_allow_html=True)
    st.caption("School performance dashboard")
    st.markdown("---")
    st.markdown('<div class="sidebar-step">01 / Upload data</div>', unsafe_allow_html=True)
    st.caption("Upload files from the main page.")

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None

if st.session_state.uploaded_files is None:
    with st.container(border=True):
        upload_columns = st.columns([1.5, 1])
        with upload_columns[0]:
            st.markdown('<div class="control-heading">Upload your dataset</div>', unsafe_allow_html=True)
            st.markdown('<div class="control-caption">Add one CSV or several files from the same school cohort. Cleaning starts automatically.</div>', unsafe_allow_html=True)
        with upload_columns[1]:
            uploaded_files = st.file_uploader(
                "Choose CSV files",
                type="csv",
                accept_multiple_files=True,
                help="CSV files may include headers, common grade formats, or score text such as marks.",
            )
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.rerun()
else:
    uploaded_files = st.session_state.uploaded_files

with st.sidebar:
    if uploaded_files:
        st.markdown(
            f'<div class="sidebar-status"><strong>{len(uploaded_files)} file(s) ready</strong><small>Cleaning and analysis are enabled</small></div>',
            unsafe_allow_html=True,
        )

if not uploaded_files:
    st.markdown('<div class="section-label">Upload data</div>', unsafe_allow_html=True)
    st.info("Upload one or more CSV files above to automatically clean and analyze your student data.")
    st.markdown("""
    **Accepted automatically**

    - CSV files with or without headers
    - Common gender and grade spellings
    - Score cells containing text such as `marks`
    - Multiple CSV parts combined into one cohort
    """)
    st.stop()

try:
    with st.status("Cleaning uploaded files...", expanded=False) as cleaning_status:
        data, cleaning = load_uploaded_data(uploaded_files)
        data = validate_data(data)
        cleaning_status.update(
            label=f"Cleaning complete: {cleaning['cleaned_rows']:,} valid rows ready",
            state="complete",
            expanded=False,
        )
except (FileNotFoundError, ValueError) as error:
    st.error(f"The uploaded dataset needs attention: {error}")
    st.stop()

if "applied_grades" not in st.session_state:
    st.session_state.applied_grades = []
if "applied_genders" not in st.session_state:
    st.session_state.applied_genders = []
if "applied_subject" not in st.session_state:
    st.session_state.applied_subject = "All subjects"

with st.container(border=True):
    heading_columns = st.columns([1.6, 1])
    with heading_columns[0]:
        st.markdown('<div class="control-heading">Analysis controls</div>', unsafe_allow_html=True)
        st.markdown('<div class="control-caption">Choose filters to update the report.</div>', unsafe_allow_html=True)
    with heading_columns[1]:
        active_count = len(st.session_state.applied_grades) + len(st.session_state.applied_genders)
        state_label = "Full cohort" if active_count == 0 else f"{active_count} filters active"
        st.markdown(f'<div class="control-state">{state_label}</div>', unsafe_allow_html=True)
    with st.form("analysis_filters"):
        filter_columns = st.columns([1.2, 1.2, 1])
        with filter_columns[0]:
            st.multiselect("Grade", list(range(1, 13)), key="grades_filter", placeholder="All grades")
        with filter_columns[1]:
            st.multiselect("Gender", sorted(data["gender"].unique()), key="gender_filter", placeholder="All genders")
        with filter_columns[2]:
            st.selectbox("Subject", ["All subjects", *SUBJECTS], key="subject_filter", format_func=str.title)
        st.markdown('<div class="control-actions"></div>', unsafe_allow_html=True)
        action_columns = st.columns([2.4, 1, 1], gap="small", vertical_alignment="center")
        with action_columns[0]:
            st.markdown('<div class="control-hint">Choose a focus, then run the analysis.</div>', unsafe_allow_html=True)
        with action_columns[1]:
            apply_filters = st.form_submit_button("Run analysis", type="primary", width="stretch")
        with action_columns[2]:
            reset_clicked = st.form_submit_button("Clear", width="stretch", on_click=reset_filter_state)

if apply_filters:
    st.session_state.applied_grades = list(st.session_state.grades_filter)
    st.session_state.applied_genders = list(st.session_state.gender_filter)
    st.session_state.applied_subject = st.session_state.subject_filter

selected_grades = st.session_state.applied_grades
selected_genders = st.session_state.applied_genders
selected_subject = st.session_state.applied_subject

with st.sidebar:
    st.markdown("---")
    st.markdown('<div class="sidebar-step">02 / Dataset health</div>', unsafe_allow_html=True)
    st.caption(
        f"{cleaning['cleaned_rows']:,} clean records · {cleaning['invalid_rows']:,} invalid · {cleaning['outlier_rows']:,} outliers removed"
    )
    st.markdown('<div class="sidebar-step">03 / Take the cleaned file</div>', unsafe_allow_html=True)
    st.download_button(
        "Download cleaned CSV",
        data=data.to_csv(index=False, quoting=csv.QUOTE_MINIMAL).encode("utf-8"),
        file_name="cleaned_student_data.csv",
        mime="text/csv",
        help="Save the validated, cleaned dataset for the school.",
    )

filtered = data.copy()
if selected_grades:
    filtered = filtered[filtered["grade"].isin(selected_grades)]
if selected_genders:
    filtered = filtered[filtered["gender"].isin(selected_genders)]

if filtered.empty:
    st.error("No students match this combination of filters.")
    st.info("Choose a different grade or gender, or reset the filters to return to the full cohort.")
    if st.button("Return to full cohort", key="empty_reset_filters"):
        st.session_state.grades_filter = []
        st.session_state.gender_filter = []
        st.session_state.subject_filter = "All subjects"
        st.rerun()
    st.stop()

st.caption(f"{cleaning['cleaned_rows']:,} clean records ready from {cleaning['uploaded_rows']:,} uploaded rows")

overview, top_students, insights, charts, quality = st.tabs(["Overview", "Top Students", "Insights", "Charts", "Data Quality"])

with overview:
    st.markdown('<div class="section-label">At a glance</div>', unsafe_allow_html=True)
    kpis = st.columns(4)
    kpis[0].metric("Students", f"{len(filtered):,}")
    kpis[1].metric("Average total", f"{filtered['total'].mean():.1f}")
    kpis[2].metric("Passing all 3", f"{passing_all_rate(filtered):.1f}%")
    kpis[3].metric("Failing at least one", f"{failing_any_rate(filtered):.1f}%")
    st.markdown('<div class="section-label">Results by grade</div>', unsafe_allow_html=True)
    grade_row = st.columns(2)
    with grade_row[0]:
        show_chart(average_total_by_grade, filtered)
    with grade_row[1]:
        show_chart(pass_rate_by_grade, filtered)
    st.markdown('<div class="insight">Use the controls above to view results for selected grades or genders.</div>', unsafe_allow_html=True)

with top_students:
    st.markdown('<div class="section-label">Leaderboard</div>', unsafe_allow_html=True)
    max_students = min(50, len(filtered))
    if st.session_state.get("top_students_limit", 1) > max_students:
        st.session_state.top_students_limit = max_students
    limit = st.slider("Students to show", min_value=1, max_value=max_students, value=min(10, max_students), key="top_students_limit")
    st.subheader("Top students share ranks when totals are tied")
    st.dataframe(ranked_students(filtered).head(limit), width="stretch", hide_index=True)
    st.subheader("Top student per grade")
    st.dataframe(top_student_per_grade(filtered), width="stretch", hide_index=True)

with insights:
    st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
    st.subheader("Key findings")
    top_record = ranked_students(filtered).iloc[0]
    subjects = subject_summary(filtered)
    strongest_subject = subjects.iloc[0]
    weakest_subject = subjects.iloc[-1]
    # Checked on the whole cleaned cohort: that is where the IQR fences were applied.
    # A small filtered subset has its own fences and would re-flag ordinary marks.
    outliers = subject_outlier_summary(data)
    total_outliers = int(outliers["outliers"].sum())
    leading_student = top_record["unique_name"].rsplit("_", 1)[0].title()
    insight_columns = st.columns(3)
    insight_columns[0].metric("Top student", leading_student)
    insight_columns[1].metric("Strongest subject", strongest_subject["subject"], f"{strongest_subject['average_score']:.1f} avg")
    insight_columns[2].metric("Priority subject", weakest_subject["subject"], f"{weakest_subject['pass_rate']:.1f}% pass rate")
    st.markdown(
        f'<div class="insight">{leading_student} is the highest-scoring student in the students currently shown, with {top_record["total"]:.0f} out of 300 total marks. '
        f'{strongest_subject["subject"]} has the highest average score. {weakest_subject["subject"]} may benefit from extra classroom support.</div>',
        unsafe_allow_html=True,
    )
    gender_data = gender_summary(filtered)
    if len(gender_data) >= 2:
        leader = gender_data.iloc[0]
        runner_up = gender_data.iloc[1]
        st.markdown(f"**Gender comparison:** In the students currently shown, {leader['gender']} students have the higher average total ({leader['average_total']:.1f} compared with {runner_up['average_total']:.1f} for {runner_up['gender']}). This describes this dataset only; it does not explain why the difference exists.")
    first_row = st.columns(2)
    with first_row[0]:
        show_chart(gender_subject_comparison, filtered)
    with first_row[1]:
        show_chart(subject_outcomes, filtered)
    st.markdown('<div class="section-label">Score checks</div>', unsafe_allow_html=True)
    outlier_columns = st.columns(2)
    outlier_columns[0].metric("Outliers removed during cleaning", f"{cleaning['outlier_rows']:,}", "IQR method", delta_color="off")
    outlier_columns[1].metric("Outliers remaining", f"{total_outliers}", "full cleaned cohort", delta_color="off")
    st.caption("Rows with any subject score or total outside the 1.5 × IQR fences are removed before analysis.")
    st.markdown(f'<div class="data-table">{outliers.to_html(index=False, float_format=lambda value: f"{value:.1f}")}</div>', unsafe_allow_html=True)
    st.subheader("Subject health")
    st.markdown(f'<div class="data-table">{subjects.to_html(index=False, float_format=lambda value: f"{value:.1f}")}</div>', unsafe_allow_html=True)

with charts:
    st.markdown('<div class="section-label">Charts</div>', unsafe_allow_html=True)
    if selected_subject == "All subjects":
        st.caption("Each chart shows how many students scored within each ten-mark range.")
        for subject in SUBJECTS:
            show_chart(score_histogram, filtered, subject)
    else:
        st.caption(f"Each bar shows how many students scored within a ten-mark range in {selected_subject.title()}.")
        show_chart(score_histogram, filtered, selected_subject)

    first_row = st.columns(2)
    with first_row[0]:
        show_chart(total_by_gender, filtered)
    with first_row[1]:
        show_chart(band_chart, performance_bands(filtered))
    second_row = st.columns(1)
    with second_row[0]:
        show_chart(correlation_heatmap, filtered)

with quality:
    st.markdown('<div class="section-label">Cleaning summary</div>', unsafe_allow_html=True)
    st.subheader("How the upload was prepared")
    quality_metrics = st.columns(4)
    quality_metrics[0].metric("Uploaded rows", f"{cleaning['uploaded_rows']:,}")
    quality_metrics[1].metric("Invalid rows removed", f"{cleaning['invalid_rows']:,}")
    quality_metrics[2].metric("Outlier rows removed", f"{cleaning['outlier_rows']:,}")
    quality_metrics[3].metric("Clean rows", f"{cleaning['cleaned_rows']:,}")
    st.markdown(
        """
        - Header names are detected and standardized automatically, and all files are combined into one cohort.
        - Names lose stray quotes and symbols and are written in Title Case, so `'navya'`, `"Navya"`, and `NAVYA` become `Navya`.
        - Gender spellings are normalized to Female or Male (`F`, `girl`, `0` → Female; `M`, `boy`, `1` → Male); anything else is Unknown.
        - Grade values such as `Grade 7` or `07` are normalized to integers 1 through 12.
        - Score cells containing text such as `marks` are converted to numbers.
        - Totals are recalculated from the three subject scores.
        - Rows with a subject score or total outside the 1.5 × IQR fences are removed as outliers.
        - Names receive a unique row identifier for reliable ranking.

        Invalid and outlier rows are removed before analysis so every chart uses validated values.
        """
    )
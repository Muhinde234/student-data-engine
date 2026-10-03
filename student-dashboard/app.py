import streamlit as st

from charts import average_total_by_grade, band_chart, correlation_heatmap, score_histogram, total_by_gender
from data import SUBJECTS, load_uploaded_data, validate_data
from metrics import failing_any_rate, passing_all_rate, performance_bands, ranked_students, top_student_per_grade


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
    h1, h2, h3, [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; color: var(--ink); }
    h1 { font-size: clamp(2.5rem, 4vw, 4.6rem); letter-spacing: -0.04em; line-height: 0.98; margin-bottom: 0.65rem; }
    h2 { font-size: 1.4rem; letter-spacing: -0.02em; }
    h3 { font-size: 1rem; letter-spacing: 0; }
    p, label, .stCaption, .stMarkdown { font-family: 'DM Sans', sans-serif; }
    .hero-kicker { color: var(--coral); font: 700 0.75rem 'DM Sans', sans-serif; letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 0.85rem; }
    .hero-copy { color: var(--muted); font-size: 1.05rem; margin-bottom: 2.25rem; max-width: 620px; }
    .hero-rule { border-top: 1px solid var(--line); margin: 0 0 1.4rem; }
    [data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-radius: 5px; padding: 1.2rem 1.3rem; box-shadow: 0 5px 18px rgba(23, 42, 58, 0.04); }
    [data-testid="stMetricLabel"] { color: var(--muted); font: 600 0.72rem 'DM Sans', sans-serif; text-transform: uppercase; letter-spacing: 0.08em; }
    [data-testid="stMetricValue"] { font-size: 2rem; margin-top: 0.35rem; }
    [data-testid="stTabs"] [role="tablist"] { gap: 1.5rem; border-bottom: 1px solid var(--line); }
    [data-testid="stTabs"] button { color: var(--muted); font: 600 0.86rem 'DM Sans', sans-serif; padding: 0.75rem 0.15rem; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: var(--ink); }
    [data-testid="stTabs"] button[aria-selected="true"] p { color: var(--coral); }
    [data-testid="stSidebar"] { background: var(--ink); border-right: 0; }
    [data-testid="stSidebar"] * { color: #f4f0ea; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #b7c2c8; }
    [data-testid="stSidebar"] .sidebar-brand { color: #f4f0ea; font: 700 1.45rem 'Space Grotesk', sans-serif; letter-spacing: -0.04em; line-height: 0.9; }
    [data-testid="stSidebar"] .sidebar-brand span { color: var(--coral); }
    [data-testid="stSidebar"] .sidebar-step { color: #e56b56; font: 700 0.68rem 'DM Sans', sans-serif; letter-spacing: 0.12em; text-transform: uppercase; margin: 1.4rem 0 0.45rem; }
    [data-testid="stSidebar"] .sidebar-status { background: #243d50; border: 1px solid #486073; border-radius: 4px; padding: 0.8rem 0.9rem; margin: 0.8rem 0 1rem; }
    [data-testid="stSidebar"] .sidebar-status strong { display: block; color: #f4f0ea; font: 600 0.9rem 'DM Sans', sans-serif; }
    [data-testid="stSidebar"] .sidebar-status small { color: #b7c2c8; font: 400 0.75rem 'DM Sans', sans-serif; }
    [data-testid="stSidebar"] .stButton button { width: 100%; background: transparent; color: #f4f0ea; border: 1px solid #486073; }
    [data-testid="stSidebar"] .stButton button:hover { border-color: var(--coral); color: #f4f0ea; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label, [data-testid="stSidebar"] [data-testid="stMultiSelect"] label { color: #f4f0ea; font-weight: 600; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div { background: #243d50; border-color: #486073; }
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] span { background: #e56b56; border: 0; }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); }
    .section-label { color: var(--coral); font: 700 0.7rem 'DM Sans', sans-serif; letter-spacing: 0.13em; text-transform: uppercase; margin: 1.7rem 0 0.35rem; }
    .insight { background: var(--ink); border-left: 4px solid var(--coral); color: #f4f0ea; padding: 1rem 1.2rem; border-radius: 3px; font: 500 0.9rem 'DM Sans', sans-serif; }
    </style>
    <div class="hero-kicker">Academic analytics / uploaded cohort</div>
    <h1>Student performance,<br>made legible.</h1>
    <div class="hero-copy">A clear read on your exam records, from grade-level trends to the students setting the pace.</div>
    <div class="hero-rule"></div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="sidebar-brand">STUDENT<br><span>SIGNAL</span></div>', unsafe_allow_html=True)
    st.caption("School performance workspace")
    st.markdown("---")
    st.markdown('<div class="sidebar-step">01 / Build your dataset</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True, help="Upload one CSV or several parts of the same dataset.")

    if uploaded_files:
        st.markdown(
            f'<div class="sidebar-status"><strong>{len(uploaded_files)} file(s) ready</strong><small>Cleaning and analysis are enabled</small></div>',
            unsafe_allow_html=True,
        )

if not uploaded_files:
    st.markdown('<div class="section-label">Ready when you are</div>', unsafe_allow_html=True)
    st.info("Upload one or more CSV files from the sidebar to automatically clean and analyze your student data.")
    st.markdown("""
    **Accepted automatically**

    - CSV files with or without headers
    - Common gender and grade spellings
    - Score cells containing text such as `marks`
    - Multiple CSV parts combined into one cohort
    """)
    st.stop()

try:
    data, cleaning = load_uploaded_data(uploaded_files)
    data = validate_data(data)
except (FileNotFoundError, ValueError) as error:
    st.error(f"The uploaded dataset needs attention: {error}")
    st.stop()

with st.sidebar:
    st.markdown("---")
    st.markdown('<div class="sidebar-step">02 / Focus the analysis</div>', unsafe_allow_html=True)
    st.caption(f"{cleaning['cleaned_rows']:,} clean records · {cleaning['removed_rows']:,} removed")
    if st.button("Reset filters"):
        st.session_state.grades_filter = []
        st.session_state.gender_filter = []
        st.session_state.subject_filter = SUBJECTS[0]
        st.rerun()
    selected_grades = st.multiselect("Grade", sorted(data["grade"].unique()), key="grades_filter")
    selected_genders = st.multiselect("Gender", sorted(data["gender"].unique()), key="gender_filter")
    selected_subject = st.selectbox("Subject", SUBJECTS, key="subject_filter")
    st.markdown('<div class="sidebar-step">03 / Take the cleaned file</div>', unsafe_allow_html=True)
    st.download_button(
        "Download cleaned CSV",
        data=data.to_csv(index=False).encode("utf-8"),
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
    st.warning("No students match these filters. Try selecting a wider range.")
    st.stop()

st.caption(f"{cleaning['cleaned_rows']:,} clean records ready from {cleaning['uploaded_rows']:,} uploaded rows")

overview, top_students, charts, quality = st.tabs(["Overview", "Top Students", "Charts", "Data Quality"])

with overview:
    st.markdown('<div class="section-label">At a glance</div>', unsafe_allow_html=True)
    kpis = st.columns(4)
    kpis[0].metric("Students", f"{len(filtered):,}")
    kpis[1].metric("Average total", f"{filtered['total'].mean():.1f}")
    kpis[2].metric("Passing all 3", f"{passing_all_rate(filtered):.1f}%")
    kpis[3].metric("Failing at least one", f"{failing_any_rate(filtered):.1f}%")
    st.markdown('<div class="section-label">Cohort trajectory</div>', unsafe_allow_html=True)
    st.subheader("Average total by grade")
    st.plotly_chart(average_total_by_grade(filtered), use_container_width=True)
    st.markdown('<div class="insight">The overview follows the cohort from grade 1 to grade 12. Use the sidebar to isolate a particular group and let every view update with it.</div>', unsafe_allow_html=True)

with top_students:
    st.markdown('<div class="section-label">Leaderboard</div>', unsafe_allow_html=True)
    max_students = min(50, len(filtered))
    limit = st.slider("Students to show", min_value=1, max_value=max_students, value=min(10, max_students))
    st.subheader("Top students share ranks when totals are tied")
    st.dataframe(ranked_students(filtered).head(limit), use_container_width=True, hide_index=True)
    st.subheader("Top student per grade")
    st.dataframe(top_student_per_grade(filtered), use_container_width=True, hide_index=True)

with charts:
    st.markdown('<div class="section-label">Explore the distributions</div>', unsafe_allow_html=True)
    first_row = st.columns(2)
    with first_row[0]:
        st.plotly_chart(score_histogram(filtered, selected_subject), use_container_width=True)
    with first_row[1]:
        st.plotly_chart(total_by_gender(filtered), use_container_width=True)
    second_row = st.columns(2)
    with second_row[0]:
        st.plotly_chart(band_chart(performance_bands(filtered)), use_container_width=True)
    with second_row[1]:
        st.plotly_chart(correlation_heatmap(filtered), use_container_width=True)

with quality:
    st.markdown('<div class="section-label">Trust the inputs</div>', unsafe_allow_html=True)
    st.subheader("How the upload was prepared")
    quality_metrics = st.columns(3)
    quality_metrics[0].metric("Uploaded rows", f"{cleaning['uploaded_rows']:,}")
    quality_metrics[1].metric("Clean rows", f"{cleaning['cleaned_rows']:,}")
    quality_metrics[2].metric("Rows removed", f"{cleaning['removed_rows']:,}")
    st.markdown(
        """
        - Header names are detected and standardized automatically.
        - Gender spellings are normalized to Female, Male, or Unknown.
        - Grade values are extracted and normalized to integers 1 through 12.
        - Score cells containing text such as `marks` are converted to numbers.
        - Totals are recalculated from the three subject scores.
        - Names receive a unique row identifier for reliable ranking.

        Invalid rows are removed before analysis so every chart uses validated values.
        """
    )
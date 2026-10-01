import streamlit as st

from charts import average_total_by_grade, band_chart, correlation_heatmap, score_histogram, total_by_gender
from data import SUBJECTS, load_data
from metrics import failing_any_rate, passing_all_rate, performance_bands, ranked_students, top_student_per_grade


st.set_page_config(page_title="Student Performance Dashboard", layout="wide")
st.title("Student Performance Dashboard")
st.caption("Explore exam results without changing the validated source data.")

try:
    data = load_data()
except (FileNotFoundError, ValueError) as error:
    st.error(f"The dashboard cannot load this dataset: {error}")
    st.stop()

with st.sidebar:
    st.header("Filters")
    selected_grades = st.multiselect("Grade", sorted(data["grade"].unique()))
    selected_genders = st.multiselect("Gender", sorted(data["gender"].unique()))
    selected_subject = st.selectbox("Subject", SUBJECTS)

filtered = data.copy()
if selected_grades:
    filtered = filtered[filtered["grade"].isin(selected_grades)]
if selected_genders:
    filtered = filtered[filtered["gender"].isin(selected_genders)]

if filtered.empty:
    st.warning("No students match these filters. Try selecting a wider range.")
    st.stop()

overview, top_students, charts, quality = st.tabs(["Overview", "Top Students", "Charts", "Data Quality"])

with overview:
    kpis = st.columns(4)
    kpis[0].metric("Students", f"{len(filtered):,}")
    kpis[1].metric("Average total", f"{filtered['total'].mean():.1f}")
    kpis[2].metric("Passing all 3", f"{passing_all_rate(filtered):.1f}%")
    kpis[3].metric("Failing at least one", f"{failing_any_rate(filtered):.1f}%")
    st.subheader("Average total by grade")
    st.plotly_chart(average_total_by_grade(filtered), use_container_width=True)

with top_students:
    limit = st.slider("Students to show", min_value=5, max_value=50, value=10)
    st.subheader("Top students share ranks when totals are tied")
    st.dataframe(ranked_students(filtered).head(limit), use_container_width=True, hide_index=True)
    st.subheader("Top student per grade")
    st.dataframe(top_student_per_grade(filtered), use_container_width=True, hide_index=True)

with charts:
    st.plotly_chart(score_histogram(filtered, selected_subject), use_container_width=True)
    st.plotly_chart(total_by_gender(filtered), use_container_width=True)
    st.plotly_chart(band_chart(performance_bands(filtered)), use_container_width=True)
    st.plotly_chart(correlation_heatmap(filtered), use_container_width=True)

with quality:
    st.subheader("How the source data was cleaned")
    st.markdown(
        """
        - Three of four source files had no header, so the shared schema was applied.
        - Twelve gender spellings were normalized to Female, Male, or Unknown.
        - Thirty-six grade formats were normalized to integers 1 through 12.
        - 4,028 score cells contained the text `marks`; the text was removed while preserving the numbers.
        - Names were not unique, so `unique_name` was created for row-level identification.

        `Unknown` gender values remain Unknown because the original 0/1 codebook was unavailable.
        """
    )
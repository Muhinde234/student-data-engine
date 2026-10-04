# Student Signal Presentation Guide

## 30-Second Project Explanation

> Student Signal is a school performance analytics dashboard. A school uploads one or more student CSV files, and the system automatically cleans and validates the records. It then helps staff understand overall performance, compare groups, identify the strongest students, find subject weaknesses, and download a trusted cleaned dataset.

The project is descriptive analytics. It uses pandas for data processing and Plotly for interactive charts. It does not train a machine-learning model or make predictions.

## The Problem

Schools often receive student results in inconsistent CSV files. Common problems include:

- Multiple files for one cohort
- Missing or inconsistent headers
- Gender labels such as `F`, `Female`, `M`, or `Male`
- Grade values stored as text
- Score cells containing text such as `marks`
- Totals that need to be recalculated
- Duplicate student names

Without cleaning, charts and rankings can be misleading. Student Signal creates one validated dataset before analysis.

## The Demonstration Flow

### 1. Start the application

From the project root:

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open the URL Streamlit prints, normally `http://localhost:8501`.

### 2. Upload data

Upload one CSV file or all four `student_data_part*.csv` files. Explain that the application accepts multiple files because a school may receive results in separate parts.

### 3. Explain automatic cleaning

Point to the dataset health information:

- Uploaded rows
- Clean rows
- Removed rows

Then open **Data Quality** and explain that the system standardizes headers, gender, grades, and scores, recalculates totals, and assigns unique row identifiers.

### 4. Show the overview

Explain the four headline metrics:

- **Students:** number of records in the current filtered cohort
- **Average total:** average Math + Science + English score
- **Passing all 3:** percentage scoring at least 40 in every subject
- **Failing at least one:** percentage scoring below 40 in one or more subjects

### 5. Demonstrate analysis controls

Select a grade or gender, choose a subject, and click **Run analysis**. Explain that the dashboard updates all metrics, tables, and charts for the selected cohort. Click **Clear** to return to the full cohort.

### 6. Show the strongest students

Open **Top Students**. Explain that rankings use competition ranking, so tied students receive the same rank. Show both the overall leaderboard and the top student in each grade.

### 7. Compare performance

Open **Charts** and explain:

- The histogram shows the selected subject's score distribution.
- The gender box plot compares total-score spread.
- The performance-band chart shows Fail, Pass, Good, and Excellent counts.
- The correlation heatmap shows relationships between subjects.

Do not claim that gender causes performance differences. Say that the dashboard reports observed differences in this uploaded dataset.

### 8. Export the result

Click **Download cleaned CSV**. Explain that the school receives a reusable, validated dataset after cleaning.

## Technical Architecture

```text
CSV uploads
    |
    v
student-dashboard/data.py
(read, normalize, clean, validate)
    |
    v
student-dashboard/metrics.py
(calculate rates, rankings, bands, summaries)
    |
    +--> student-dashboard/charts.py
    |    (build Plotly figures)
    |
    v
student-dashboard/app.py
(Streamlit UI, filters, tabs, download)
```

`streamlit_app.py` is only the root launcher. The main interface lives in `student-dashboard/app.py`.

## Important Cleaning Rules

- Header names are normalized to the expected schema.
- Headerless files are read using the expected source-column order.
- Gender values are mapped to `Female`, `Male`, or `Unknown`.
- Grade numbers are extracted and restricted to 1 through 12.
- Scores are converted to numbers and must be between 0 and 100.
- Invalid rows are removed before analysis.
- `total` is recalculated as Math + Science + English.
- `student_id` is generated for every cleaned row.
- `unique_name` prevents duplicate names from breaking rankings.

## How To Answer Common Questions

### Is this machine learning?

No. It is a data cleaning and descriptive analytics application. It summarizes historical records; it does not predict future performance.

### Why are some rows removed?

Rows are removed when they do not have a usable grade or valid subject scores. This prevents invalid values from affecting school metrics.

### Why recalculate the total?

The total is recalculated from the subject scores so the dashboard uses a consistent and auditable definition.

### How is passing defined?

A student passes a subject at 40 or above. Passing all three means Math, Science, and English are all at least 40.

### How is the best student identified?

Students are ranked by descending total score. Ties share the same competition rank.

### Does the dashboard prove that one gender performs better?

No. It compares observed averages, distributions, and pass rates in the uploaded data. It should not be interpreted as causal evidence.

### Can the school upload only one file?

Yes. The dashboard accepts one file or multiple CSV files and does not impose a fixed record-count limit.

### What happens if a filter has no matching records?

The dashboard shows a clear no-results message and provides a way to return to the full cohort.

## Professional Strengths

- Reusable: works with new school CSV files.
- Auditable: cleaning rules are explicit and the cleaned file can be downloaded.
- Interactive: filters update the entire analysis workflow.
- Practical: supports rankings, subject review, group comparison, and grade trends.
- Defensive: validates data and handles small or empty filtered cohorts.
- Tested: ranking, pass/fail rates, and performance bands have automated tests.

## Honest Limitations And Future Work

- The gender comparison is descriptive and should be interpreted carefully.
- The current pass threshold is fixed at 40; a school could make this configurable.
- The current source schema expects Math, Science, and English; future versions could support configurable subjects.
- There is no authentication or database persistence yet.
- Future versions could add PDF reports, school branding, year-over-year comparisons, and role-based access.

## Closing Statement

> The key value is not only the charts. It is the complete path from messy school files to a cleaned, validated, explainable dataset and then to decisions that staff can understand.

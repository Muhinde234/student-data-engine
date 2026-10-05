# Student Signal: Complete Study Guide

## 1. The One-Sentence Answer

Student Signal is a Streamlit school-results dashboard that cleans uploaded CSV files, validates the records, calculates performance metrics, and presents rankings, charts, and findings for school staff.

## 2. What Problem Does It Solve?

Schools may receive results in separate files with inconsistent formatting. For example:

- A file may have headers while another does not.
- Gender may be written as `F`, `Female`, `M`, or `Male`.
- Grade may be stored as text such as `Grade 6`.
- Scores may contain text such as `marks`.
- Student names may repeat.
- Uploaded totals may be incorrect or inconsistent.

The application creates one clean and validated dataset before showing results. This prevents charts and rankings from being based on invalid values.

## 3. Is It Machine Learning?

No. This is **data cleaning and descriptive analytics**.

It does not:

- Train a model
- Predict future grades
- Classify students with artificial intelligence
- Prove that one group causes another group to perform better

It describes the records that the school uploads.

A strong presentation sentence is:

> The system transforms raw school records into a clean dataset and uses descriptive statistics to help staff understand performance.

## 4. Understand The Files

### `streamlit_app.py`

This is the root launcher. It adds the `student-dashboard` folder to Python's import path and runs `app.py`.

It exists so the application can be started from the project root with:

```powershell
python -m streamlit run streamlit_app.py
```

It does not contain the dashboard logic.

### `student-dashboard/app.py`

This is the user interface and application flow. It:

1. Configures the Streamlit page.
2. Defines the visual styling.
3. Shows the upload control.
4. Calls the cleaning pipeline.
5. Shows the analysis controls.
6. Applies grade and gender filters.
7. Displays metrics, tables, tabs, and charts.
8. Offers the cleaned CSV for download.

`app.py` connects the other modules together.

### `student-dashboard/data.py`

This owns uploaded data.

Important functions:

- `_column_key`: makes column names comparable by removing case and punctuation.
- `_read_upload`: reads a CSV with a header or a headerless CSV.
- `clean_data`: combines files and normalizes the records.
- `load_uploaded_data`: cached entry point used by the app.
- `validate_data`: checks the final cleaned schema and value ranges.

Cleaning sequence:

```text
Upload files
  -> Read each file
  -> Combine rows
  -> Standardize columns
  -> Normalize names and gender
  -> Extract numeric grades
  -> Extract numeric subject scores
  -> Remove invalid rows
  -> Recalculate totals
  -> Create IDs
  -> Validate final data
```

### `student-dashboard/metrics.py`

This contains calculations that do not depend on Streamlit. Keeping calculations here makes them easier to test.

Important functions:

- `passing_all_rate`: percentage of students with every subject at least 40.
- `failing_any_rate`: percentage with at least one subject below 40.
- `ranked_students`: sorts students by total and gives tied students the same competition rank.
- `performance_bands`: counts Fail, Pass, Good, and Excellent marks.
- `top_student_per_grade`: finds the highest-ranked student or tied students in each grade.
- `gender_summary`: compares group size, subject averages, totals, and all-subject pass rates.
- `subject_summary`: compares average marks, pass rates, and excellent rates.
- `grade_summary`: summarizes student count, average total, and pass rate by grade.
- `subject_outlier_summary`: identifies statistical outliers using the 1.5 IQR rule.

### `student-dashboard/charts.py`

This contains Plotly chart builders. Each function receives a cleaned DataFrame and returns a Plotly figure.

Charts include:

- Average total by grade
- Score ranges by subject
- Total-score spread by gender
- Performance bands by subject
- Subject score relationships
- Average subject scores by gender
- Subject average score versus pass rate

`polish` applies shared fonts, colors, spacing, axes, hover styling, and chart dimensions.

### `student-dashboard/tests/`

These tests protect calculation behavior.

Current coverage includes:

- Tied ranking behavior
- Pass and fail rates
- Performance-band counts
- Score chart ranges and boundaries

Run them with:

```powershell
cd student-dashboard
..\.venv\Scripts\python.exe -m pytest -q tests
```

### `requirements.txt`

The application uses:

- `pandas` for tables and calculations
- `plotly` for interactive charts
- `streamlit` for the web interface
- `pytest` for tests

## 5. Data Contract

The source data is expected to contain:

```text
name, gender, grade, math, science, english, total
```

The cleaned internal schema is:

```text
student_id, unique_name, name, gender, grade, math, science, english, total
```

The application does not trust the uploaded total. It recalculates:

```text
Total = Math + Science + English
```

Scores must be between 0 and 100. Grades must be between 1 and 12.

## 6. Metric Formulas

### Average total

```text
Average total = sum of student totals / number of students
```

### Passing all three subjects

A student passes all three when:

```text
Math >= 40 AND Science >= 40 AND English >= 40
```

The percentage is:

```text
students passing all three / total students * 100
```

### Failing at least one subject

A student fails at least one when:

```text
Math < 40 OR Science < 40 OR English < 40
```

### Performance bands

- Fail: 0–39
- Pass: 40–59
- Good: 60–79
- Excellent: 80–100

### Competition ranking

If totals are `240, 120, 120`, the ranks are:

```text
1, 2, 2
```

The tied students share rank 2.

### Outliers

The application uses the IQR method:

```text
IQR = Q3 - Q1
Lower boundary = Q1 - 1.5 * IQR
Upper boundary = Q3 + 1.5 * IQR
```

An outlier is a value outside those boundaries. An outlier is a statistical flag, not automatically an error.

## 7. What Each Dashboard Area Means

### Upload area

Upload one CSV or several files. The files are combined into one dataset.

### Overview

Shows the main numbers for the current selection:

- Number of students
- Average total
- Percentage passing all three
- Percentage failing at least one
- Average total by grade

### Top Students

Shows:

- Overall ranking
- Subject scores
- Total score
- Top student in each grade

### Insights

Shows plain-language findings:

- Highest-scoring student
- Strongest subject
- Subject needing the most support
- Observed gender comparison
- Subject score outlier count
- Subject health table

### Charts

Shows visual patterns in:

- Score ranges
- Gender score spread
- Performance bands
- Subject relationships

### Data Quality

Explains what happened during cleaning:

- How many rows were uploaded
- How many clean rows remain
- How many rows were removed
- Which standardization rules were applied

## 8. How To Demonstrate It

Use this order during the presentation:

1. Start the application.
2. Upload all four sample CSV files.
3. Point out the cleaning summary.
4. Explain the four overview metrics.
5. Filter to one grade and click **Run analysis**.
6. Open **Top Students** and show the ranking.
7. Open **Insights** and explain the strongest and weakest subjects.
8. Open **Charts** and explain one chart.
9. Use the chart toolbar to zoom or reset the chart.
10. Open **Data Quality**.
11. Download the cleaned CSV.
12. Click **Clear** and return to the full dataset.

## 9. How To Explain The Score-Range Chart

Say:

> The horizontal labels are ten-mark ranges. Each bar shows how many students scored in that range. A taller bar means more students received marks in that range. The average mark gives us the center of the group.

Do not say that the chart predicts performance. It only describes the uploaded marks.

## 10. How To Explain Gender Results

Say:

> The dashboard compares the observed averages and score distributions for the gender labels in this dataset. It does not prove that gender causes the difference, and the result may change with another school or another group of students.

This is important because the dashboard reports association, not causation.

## 11. Common Questions And Answers

### Why does the app clean the data?

Because inconsistent labels, invalid scores, and incorrect totals can produce misleading results.

### Why does the app accept multiple files?

Schools may receive one cohort split across several CSV files. Combining them makes the analysis complete.

### Why are duplicate names allowed?

Names are not always unique. The app creates `unique_name` so every row can be ranked separately.

### Why is the total recalculated?

To make the result auditable and consistent with the three subject marks.

### What happens to invalid rows?

Rows with unusable grades or subject scores outside 0–100 are removed before analysis, and the number removed is displayed.

### Why can a filter show no students?

Because the selected combination may not exist in the uploaded file. The app shows a recovery message instead of treating that as a data error.

### Is a high score automatically an outlier?

No. A score of 100 can be valid. The outlier check is statistical and separate from the score-validity check.

### Why are there no predictions?

The project focuses on reliable reporting and data quality. Prediction would require a separate model, training data, evaluation, and fairness checks.

## 12. What Makes The Project Strong

- It solves a real school data problem.
- It supports new uploads instead of only one fixed file.
- It keeps cleaning and calculations separate from the UI.
- It validates records before analysis.
- It gives the school a cleaned file to reuse.
- It explains results in plain language.
- It includes tests for important calculations.
- It handles filters and small result sets defensively.

## 13. Honest Limitations

Say these confidently if asked:

- It is a local or hosted prototype, not yet a full school information system.
- It has no login or role-based access.
- It does not store data permanently in a database.
- The pass mark is currently fixed at 40.
- The current schema supports Math, Science, and English.
- Gender analysis is descriptive, not causal.
- More tests would be needed for a production release.

## 14. Five-Minute Speaking Script

> Good morning. My project is Student Signal, a school performance analytics dashboard.
>
> The problem is that school results often arrive in separate CSV files and may contain inconsistent headers, gender labels, grade formats, score text, duplicate names, or unreliable totals.
>
> The first stage of my system is data preparation. It combines the uploaded files, standardizes the columns, converts grades and marks to usable values, removes invalid rows, recalculates totals, and creates unique identifiers for students.
>
> The second stage is analysis. The dashboard reports the number of students, average total score, the percentage passing all subjects, and the percentage failing at least one subject.
>
> The school can filter by grade, gender, and subject. The Top Students page ranks students by total score and handles ties correctly. The Insights page highlights the highest-scoring student, strongest subject, subject needing support, gender comparison, and score-quality checks.
>
> The Charts page gives visual views of score ranges, gender score spread, performance bands, and relationships between subjects.
>
> This is descriptive analytics, not machine learning. It explains the data that was uploaded; it does not predict the future or claim that one gender causes performance differences.
>
> Finally, the school can download the cleaned and validated CSV for future use. The main value is the complete path from messy records to understandable and auditable school decisions.

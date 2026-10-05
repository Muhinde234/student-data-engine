# Student Signal

Student Signal is a Streamlit dashboard for cleaning and analyzing school performance data. A school can upload one CSV file or several CSV parts, receive a cleaned dataset, and explore cohort performance through metrics, charts, and rankings.

## What The Project Does

1. Uploads one or more student CSV files.
2. Detects files with standard headers or no headers.
3. Normalizes names, gender labels, grades, and score values.
4. Removes invalid rows and IQR outliers, and recalculates totals.
5. Validates the cleaned dataset before analysis.
6. Shows school-level metrics, grade trends, subject distributions, gender comparisons, and top students.
7. Exports the cleaned dataset as `cleaned_student_data.csv`.

This is descriptive analytics, not machine learning. The dashboard summarizes the records provided by the school; it does not train or predict a model.

## Project Structure

```text
project-presentation/
|-- streamlit_app.py                 # Canonical root launcher
|-- student-dashboard/
|   |-- app.py                        # Streamlit interface and page layout
|   |-- data.py                       # Upload, cleaning, and validation pipeline
|   |-- metrics.py                    # Reusable school-performance calculations
|   |-- charts.py                     # Plotly chart builders and shared styling
|   |-- requirements.txt              # Python dependencies
|   `-- tests/test_metrics.py         # Metric regression tests
|-- student_data_part*.csv            # Optional local sample files
```

## Run The Dashboard

From the project root, activate the virtual environment and run the single canonical launcher:

```powershell
cd "C:\Users\IGIRIMPUHWE Dositha\Desktop\project-presentation"
.\.venv\Scripts\Activate.ps1
python -m streamlit run streamlit_app.py
```

Then open the URL printed by Streamlit, normally:

```text
http://localhost:8501
```

Use one running Streamlit process at a time. If another process is already using port 8501, stop it or use the port shown by Streamlit.

## Dashboard Workflow

- **Upload:** Choose one or more CSV files in the main workspace.
- **Clean:** The app standardizes the uploaded records automatically.
- **Control:** Select grades, gender, and subject, then click **Run analysis**.
- **Explore:** Use Overview, Top Students, Charts, and Data Quality tabs.
- **Export:** Download the validated cleaned CSV from the sidebar.

## Accepted Data

The source files should contain these fields, with or without a header row:

```text
name, gender, grade, math, science, english, total
```

The cleaner accepts common variations such as `F`/`Female`, `M`/`Male`, grade text containing a number, and score values containing text such as `marks`. Totals are recalculated from Math + Science + English, so the uploaded total is not trusted blindly.

## Validation And Tests

Run the checks from the project root:

```powershell
cd student-dashboard
..\.venv\Scripts\python.exe -m py_compile app.py data.py charts.py streamlit_app.py
..\.venv\Scripts\python.exe -m pytest -q tests
```

The tests currently cover ranking ties, pass/fail rates, and performance-band counts.

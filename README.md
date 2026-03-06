# Maestro Dashboard

Maestro Dashboard is a visualization tool built on the **Streamlit** framework, designed to clearly display the results of automated tests (Maestro). The application parses XML reports, JSON files, and logs, providing success statistics, interactive charts, and detailed error previews for Android, iOS, and API platforms.

---

## Main Features

* **Project Selection:** The landing page allows switching between the **Volkswagen** dashboard and the **Škoda** placeholder section.

* **Multi-platform Support:** Switch between Android, iOS, and API test results using a radio button selector.

* **API Test Report (⚙️ API):**
  * Reads JSON test result files from `logs/json`.
  * Displays an **In-App Shop Cart API Test Report** with a live timestamp.
  * Two tabs: **Summary charts** (filterable by status) and **All results** (grouped by test name).
  * Each result shows Run ID, duration, error message, and a full JSON detail view.

* **Interactive Calendar:** Filter test runs by date using a visual monthly calendar. Days with available runs are highlighted; the selected day is marked in blue.

* **Run Selector:** After selecting a date, a dropdown lists all available test run IDs for that day (sorted newest first).

* **Global Overview:** Summary statistics (Total, Passed, Failed, Success Rate) for the entire platform history, with interactive charts and filterable test folder breakdown.

* **Detailed Run Analysis:**
  * Per-run metrics: Total, Passed, Failed, Success Rate.
  * Pie chart for pass/fail ratio.
  * Bar chart for average duration per test.
  * Filterable breakdown of test folders by status.

* **Error Inspection:**
  * Color highlighting of error messages in logs (ERROR, FATAL, EXCEPTION, FAIL, WARN).
  * Display of failure screenshots (`fail_{test_name}.png`) for failed tests.
  * Access to the full content of `console_output.log`.

---

## Project Structure

```text
├── app.py                 # Main application entry point
├── src/
│   ├── components.py      # UI components (metrics, charts, log viewer)
│   └── data_provider.py   # XML/JSON/log file loading and parsing
├── logs/                  # Input data directory (see below)
│   ├── logs_android/
│   ├── logs_ios/
│   └── json/
└── requirements.txt       # List of dependencies
```

---

## Requirements

* Python 3.9+
* Libraries listed in `requirements.txt`: Streamlit, Pandas, Plotly, Pillow, Streamlit Calendar, streamlit-plotly-events.

---

## Installation and Setup

**1. Clone the repository:**

```text
git clone <repository-url>
cd maestro-dashboard
```

**2. Create a virtual environment (recommended):**

```text
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

**3. Install dependencies:**

```text
pip install streamlit pandas plotly streamlit-calendar streamlit-plotly-events
```

**4. Run the application:**

```text
streamlit run app.py
```

---

## Data Organization (Logs Directory)

The application expects a specific folder structure inside the `logs` directory. Strict naming conventions must be followed for data to load correctly.

### Android / iOS

```text
logs/
├── logs_android/                        # Data for the Android section
│   └── <run_id>/                        # Run folder (e.g., 2026-02-13_06-09-21)
│       ├── report_1.xml                 # Test result (JUnit XML)
│       ├── fail_<test_name>.png         # Failure screenshot (optional)
│       └── console_output.log           # Text log of the test
│
└── logs_ios/                            # Data for the iOS section
    └── <run_id>/
        ├── report_1.xml
        └── ...
```

### API

```text
logs/
└── json/                                # Data for the API section
    └── <timestamp>.json                 # e.g., 20260217_0828.json
```

---

## File Formats

### XML Reports (Android / iOS)
The application parses standard **JUnit XML** output. Key attributes: `testcase name`, `time`, and the `failure` element for error detection. The run ID is derived from the folder name (a date/timestamp is expected at the start).

### JSON Reports (API)
Each JSON file must contain a list with at least one object. The object should have a `results` array where each entry includes:
* `name` — test name
* `status` — `"pass"` or other value (mapped to Passed / Failed)
* `runDuration` — duration in seconds
* `testResults` — array with optional `description` for failed steps
* `response.status` — HTTP status code

The run ID is taken from the first 13 characters of the filename (e.g., `20260217_0828`).

### Screenshots
For failed mobile tests, the application looks for `fail_{test_name}.png` inside the run folder.

### Logs
To display detailed console output, a file named `console_output.log` must be present in the run folder. Lines containing `ERROR`, `FATAL`, `EXCEPTION`, or `FAIL` are highlighted in red; `WARN` lines are highlighted in orange.

---

## Application Logic

* **`data_provider.py`**
  * `get_all_test_data(platform_selection)` — scans the appropriate folder (`logs_android`, `logs_ios`, or `logs/json`) based on the selected platform, parses all results, and returns a unified Pandas DataFrame. Results are cached for 10 minutes (`@st.cache_data(ttl=600)`).
  * `get_log_content(folder_path, filename)` — reads a log file and returns its lines, or an error message if the file is not found.

* **`components.py`**
  * `render_metrics(df)` — displays three metric tiles: Total tests, Success Rate, Average duration.
  * `render_charts(df, key_suffix)` — renders a pie chart (pass/fail ratio) and a bar chart (average duration per test). Returns the selected status filter from the dropdown, or `None` if no filter is active.
  * `highlight_logs(lines)` — renders log lines in a styled HTML block with color-coded error/warning keywords.

* **`app.py`**
  * Manages navigation between the landing page, Škoda placeholder, and the main VW dashboard using `st.session_state`.
  * Handles platform selection (Android / iOS / API) and routes to the appropriate rendering section.
  * For mobile platforms: renders calendar, run selector, global history, and per-run detail.
  * For API: renders tabbed report with summary charts and full result listing.

---

## Troubleshooting

* **Error: No data found**
  * Verify that the `logs` folder exists in the project root directory.
  * For mobile: confirm subdirectories are named exactly `logs_android` and `logs_ios`.
  * For API: confirm the `logs/json` folder exists and contains valid `.json` files.
  * Check that XML/JSON files are not corrupted.

* **Error: Screenshots are not appearing**
  * Ensure the screenshot file is named `fail_{test_name}.png` and is placed inside the correct run folder.

* **Error: Log not displaying**
  * Ensure the file is named exactly `console_output.log` and is located inside the run folder.

* **API data not loading**
  * Confirm the JSON file contains a list as the root element with at least one object.
  * Check that the `results` array exists and entries have the expected fields (`name`, `status`, `runDuration`).

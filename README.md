# Maestro Dashboard

Maestro Dashboard is a visualization tool built on the **Streamlit** framework, designed to clearly display the results of automated tests (Maestro). The application parses XML reports and logs, providing success statistics, interactive charts, and detailed error previews for Android and iOS platforms.

## Main Features
* **Multi-platform Support:** Switch between Android and iOS results.
  
* **Interactive Calendar:** Filter test runs by date using a visual calendar.
  
* **Global Overview:** Summary statistics (Total, Passed, Failed, Success Rate) for the entire testing history.
  
* **Detailed Run Analysis:**
  * Pie charts for success ratios.
  * Bar charts for the average duration of individual tests.
    
* **Error Inspection:**
  * Color highlighting of error messages in logs (Error, Fatal, Exception).
  * Display of failure screenshots for failed tests.
  * Access to the full content of `console_output.log`.

## Project Structure
The application is divided into logical modules to separate data loading logic, rendering, and the interface itself.

```text
├── app.py                 # Main application entry point
├── src/
│   ├── components.py      # UI components (metrics, charts, log viewer)
│   └── data_provider.py   # XML/log file loading and parsing
├── logs/                  # Input data directory (see below)
│   ├── logs_android/
│   └── logs_ios/
└── requirements.txt       # List of dependencies
```

## Requirements
* Python 3.9+
* Libraries listed in requirements.txt (specifically Streamlit, Pandas, Plotly, Pillow, Streamlit Calendar).

## Installation and Setup
* **1. Cloning the repository:**

```text
git clone <url-repozitare>
cd maestro-dashboard
```

* **2. Creating a virtual environment (recommended):**

```text
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

* **3. Installing dependencies:**

```text
pip install streamlit pandas plotly streamlit-calendar
```

* **4. Running the application:**

```text
streamlit run app.py
```

## Data Organization (Logs Directory)
For the application to load data correctly, strict folder structure must be adhered to within the `logs` directory. The application expects XML reports (JUnit format) and optional screenshots/logs.
The structure must look as follows:
```text
logs/
├── logs_android/                     # Data for the Android section
│   └── <timestamp_nebo_id_behu>/     # Specific run folder (e.g., 2026-02-13_06-09-21)
│       ├── report_1.xml              # Test result (JUnit XML)
│       ├── fail_1.png                # Error screenshot (optional, must match test ID)
│       └── console_output.log        # Text log of the test
│
└── logs_ios/                         # Data for the iOS section
    └── <timestamp_nebo_id_behu>/
        ├── report_1.xml
        └── ...
```

## File Formats

* **XML Reports**: The application parses standard JUnit XML output. Key attributes are `testcase name`, `time`, and the `failure` element for error detection.

* **Screenshots**:If a test fails, the application looks for an image in the format `fail_{ID}.png`, where `{ID}` corresponds to the number in the XML file name (e.g., for `report_123.xml` it searches for `fail_123.png`).

* **Logs**: To display a detailed output, a file named `console_output.log` is expected.


## Application Logic
* **Data Loading**: The `data_provider.py` script scans the `logs_android` or `logs_ios` folders based on the user's selection.

* **Calendar:** Events are generated in the calendar based on folder names (a date in YYYY-MM-DD format is expected at the beginning of the folder name).

* **Visualization:**

  * `render_metrics`: Calculates success rate and average times.
  * `highlight_logs`: Scans log text and applies HTML styling to lines containing keywords like "ERROR" or "FAIL".


## Troubleshooting
* **Error: No data found**

  * Verify that a `logs` folder exists in the project directory.
  * Verify that subdirectories are named exactly `logs_android` and `logs_ios`.
  * Check if the XML files are not corrupted.

* **Error: Screenshots are not appearing**

  * Ensure the screenshot name follows the `fail_{test_id}.png` convention. The test ID is derived from the XML filename (e.g., `report_5.xml` -> ID `5`).

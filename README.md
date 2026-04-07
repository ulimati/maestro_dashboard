# Maestro Dashboard

Maestro Dashboard is an interactive visualization tool built with **Streamlit**, designed for QA teams to analyze automated test results across multiple platforms in one place.

The application processes XML reports, JSON files, and logs, and provides clear insights through charts, metrics, and detailed error inspection.

---

## Main Features

* Multi-platform test visualization (**Android, iOS, API**)
* Interactive filtering by date, run ID, and status
* Detailed error inspection (logs + screenshots)
* API test reporting from JSON files
* User authentication with MongoDB (bcrypt hashed passwords)

---

## Authentication & Database

The application uses **MongoDB** for user management.

* Users are stored in a `users` collection
* Passwords are securely hashed using **bcrypt**
* Login is required to access the dashboard

### Local setup for database

Create a file:

```
.streamlit/secrets.toml
```

Add:

```toml
MONGO_URI = "your_mongodb_connection_string"
```

---

## Tech Stack

* Python
* Streamlit
* MongoDB (Atlas)
* pymongo
* bcrypt
* Pandas
* Plotly

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/maestro-dashboard.git
cd maestro-dashboard
```

---

### 2. Create virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the application

```bash
streamlit run app.py
```

---

## Project Structure

```
├── app.py
├── src/
│   ├── components.py
│   ├── data_provider.py
│   └── db.py
├── logs/
│   ├── logs_android/
│   ├── logs_ios/
│   └── json/
├── .streamlit/
│   └── secrets.toml   # NOT tracked in git
└── requirements.txt
```

---

## Data Organization

### Android / iOS

```
logs/
├── logs_android/
│   └── <run_id>/
│       ├── report_1.xml
│       ├── fail_<test_name>.png
│       └── console_output.log
```

### API

```
logs/
└── json/
    └── <timestamp>.json
```

---

## File Formats

### XML Reports

* Standard **JUnit XML**
* Required fields:

  * `testcase name`
  * `time`
  * `failure` element

---

### JSON Reports

Each file must contain:

* `results` array with:

  * `name`
  * `status`
  * `runDuration`
  * optional `testResults.description`
  * `response.status`

---

### Logs & Screenshots

* Logs: `console_output.log`
* Screenshots: `fail_<test_name>.png`

Error keywords are highlighted automatically:

* 🔴 ERROR / FAIL / EXCEPTION
* 🟠 WARN

---

## Application Logic

### `data_provider.py`

* Loads and parses XML, JSON, and logs
* Returns unified Pandas DataFrame
* Cached for performance

### `components.py`

* Renders charts and metrics
* Handles filtering and UI elements
* Highlights logs visually

### `db.py`

* MongoDB connection (cached)
* User authentication
* Role handling

### `app.py`

* Main app controller
* Navigation and session handling
* Platform switching (Android / iOS / API)

---

## Troubleshooting

### No data found

* Check `logs` folder structure
* Verify file formats

### Screenshots not showing

* Ensure correct naming: `fail_<test_name>.png`

### Logs not displaying

* File must be named `console_output.log`

### MongoDB connection issues

* Check `MONGO_URI` in `secrets.toml`
* Ensure cluster is accessible

---

## Security Notes

* Never commit `.streamlit/secrets.toml`
* Store credentials only in secrets
* Passwords are hashed using bcrypt

---

## Future Improvements

* User registration
* Password reset
* Advanced analytics & aggregation
* Deployment to Streamlit Cloud

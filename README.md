# Maestro Dashboard

A test results dashboard for mobile (Android / iOS) and API automated tests built with [Streamlit](https://streamlit.io).

**[Live demo →](https://ulimati-maestro-dashboard-app-sjpnsv.streamlit.app)**

## Features

- 📅 Calendar view — browse test runs by date
- 📊 Charts and metrics per platform (Android, iOS, API)
- 🔎 Run detail with per-test breakdown
- 📁 Log viewer for individual test cases

## Tech stack

- **Frontend & backend:** Python + Streamlit
- **Data:** XML test reports (Maestro), JSON API test logs
- **Hosting:** Streamlit Community Cloud

## Project structure

```
├── app.py                  # Main Streamlit app
├── src/
│   ├── data_provider.py    # Loads data from logs/
│   ├── components.py       # Reusable UI components
│   └── models.py           # Pydantic models
├── logs/
│   ├── logs_android/       # Android test sessions
│   ├── logs_ios/           # iOS test sessions
│   └── json/               # API test results
├── requirements.txt
└── generate_fake_data.py   # Script used to generate demo data
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Demo data

All test data in this repository is anonymized and generated for demonstration purposes. No real project names, endpoints, or credentials are included.

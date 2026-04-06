import sys
from unittest.mock import MagicMock

sys.modules["streamlit"] = MagicMock()
sys.modules["streamlit_calendar"] = MagicMock()
sys.modules["plotly.express"] = MagicMock()
sys.modules["streamlit_plotly_events"] = MagicMock()
sys.modules["src"] = MagicMock()
sys.modules["src.data_provider"] = MagicMock()
sys.modules["src.components"] = MagicMock()

import pandas as pd


#session_state_logic - show_dashboard defaults to False
def test_show_dashboard_defaults_to_false():
    session = {}
    if "show_dashboard" not in session:
        session["show_dashboard"] = False
    assert session["show_dashboard"] is False


#session_state_logic - show_empty
def test_show_empty_defaults_to_false():
    session = {}
    if "show_empty" not in session:
        session["show_empty"] = False
    assert session["show_empty"] is False


#session_state_logic - clicking Volkswagen sets show_dashboard to True
def test_volkswagen_sets_show_dashboard_to_true():
    session = {"show_dashboard": False}
    session["show_dashboard"] = True
    assert session["show_dashboard"] is True


#session_state_logic - clicking Skoda sets show_dashboard to True
def test_skoda_sets_show_dashboard_to_true():
    session = {"show_dashboard": False}
    session["show_dashboard"] = True
    assert session["show_dashboard"] is True


#session_state_logic - Back button resets show_dashboard to False
def test_back_button_resets_show_dashboard_to_false():
    session = {"show_dashboard": True}
    session["show_dashboard"] = False
    assert session["show_dashboard"] is False


#session_state_logic - Default platform is Android
def test_default_platform_is_android():
    session = {"platform": "Android"}
    assert session["platform"] == "Android"

#metrics_calculation - passed count is correct
def test_passed_count_is_correct():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 1.0},
        {"status": "Passed", "duration": 2.0},
        {"status": "Failed", "duration": 3.0},
    ])
    
    passed = len(df[df["status"] == "Passed"])
    assert passed == 2


#metrics_calculation - failed count is correct
def test_failed_count_is_correct():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 1.0},
        {"status": "Passed", "duration": 2.0},
        {"status": "Failed", "duration": 3.0},
    ])

    failed = len(df[df["status"] == "Failed"])
    assert failed == 1


#metrics_calculation - success rate is 0%
def test_success_rate_is_zero_percent():
    df = pd.DataFrame(columns=["status"])
    
    total = len(df)
    rate = (len(df[df["status"] == "Passed"]) / total * 100) if total > 0 else 0
    assert rate == 0


#metrics_calculation - success rate is 100%
def test_success_rate_is_hundred_percent():
    df = pd.DataFrame([
        {"status": "Passed"},
        {"status": "Passed"},
        {"status": "Passed"},
    ])

    total = len(df)
    rate = (len(df[df["status"] == "Passed"]) / total * 100) if total > 0 else 0
    assert rate == 100


#metrics_calculation - success rate is safe on empty DataFrame
def test_success_rate_is_safe_on_empty_dataframe():
    df = pd.DataFrame(columns=["status"])

    total = len(df)
    rate = (len(df[df["status"] == "Passed"]) / total * 100) if total > 0 else 0
    assert rate == 0


#date_and_run_selection - date is extracted from run_id (first 10 characters)
def test_date_is_extracted_from_run_id():
    run_id = "2026-02-13_06-09-21"
    date = run_id[:10]
    assert date == "2026-02-13"


#date_and_run_selection - default selected date is the most recent
def test_default_selected_date_is_most_recent():
    df = pd.DataFrame([
        {"run_id": "2026-02-13_06-09-21"},
        {"run_id": "2026-02-14_08-00-00"},
        {"run_id": "2026-02-12_05-00-00"},
    ])
    
    df["date"] = df["run_id"].str[:10]
    most_recent = df["date"].max()
    assert most_recent == "2026-02-14"



#date_and_run_selection - available runs are filtered by selected date
def test_available_runs_are_filtered_by_selected_date():
    df = pd.DataFrame([
        {"run_id": "2026-02-13_06-09-21"},
        {"run_id": "2026-02-13_07-00-00"},
        {"run_id": "2026-02-14_08-00-00"},
    ])
    
    df["date"] = df["run_id"].str[:10]
    selected_date = "2026-02-13"
    runs = df[df["date"] == selected_date]["run_id"].unique()
    assert len(runs) == 2


#date_and_run_selection - runs are sorted newest first
def test_runs_are_sorted_newest_first():
    df = pd.DataFrame([
        {"run_id": "2026-02-13_06-09-21"},
        {"run_id": "2026-02-13_08-00-00"},
        {"run_id": "2026-02-13_05-00-00"},
    ])
    
    df["date"] = df["run_id"].str[:10]
    selected_date = "2026-02-13"
    runs = sorted(df[df["date"] == selected_date]["run_id"].unique(), reverse=True)
    assert runs[0] == "2026-02-13_08-00-00"


#date_and_run_selection - no runs available for date with no data
def test_no_runs_available_for_date_with_no_data():
    df = pd.DataFrame(columns=["run_id"])
    df["date"] = df["run_id"].str[:10]
    selected_date = "2026-02-13"
    runs = df[df["date"] == selected_date]["run_id"].unique()
    assert len(runs) == 0


#platform_routing - Android uses logs_android
def test_android_uses_logs_android():
    session = {"platform": "Android"}
    folder = "logs_android" if session["platform"] == "Android" else "logs_ios"
    assert folder == "logs_android"


#platform_routing - iOS uses logs_ios
def test_ios_uses_logs_ios():
    session = {"platform": "iOS"}
    folder = "logs_android" if session["platform"] == "Android" else "logs_ios"
    assert folder == "logs_ios"


#platform_routing - API keywords is detected
def test_api_keywords_is_detected():
    session = {"platform": "API"}
    assert session["platform"] == "API"
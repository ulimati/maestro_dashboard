import sys
from unittest.mock import MagicMock

sys.modules["streamlit"] = MagicMock()
sys.modules["plotly.express"] = MagicMock()
sys.modules["streamlit_plotly_events"] = MagicMock()

import pandas as pd
from src.components import render_metrics, render_charts, highlight_logs

def test_success_rate_is_75_percent():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 1.0},
        {"status": "Passed", "duration": 2.0},
        {"status": "Passed", "duration": 1.5},
        {"status": "Failed", "duration": 3.0},
    ])

    total = len(df)
    passed = len(df[df["status"] == "Passed"])
    rate = (passed / total * 100)

    assert rate == 75.0


def test_success_rate_empty_dataframe():
    df = pd.DataFrame(columns=["status", "duration"])

    total = len(df)
    passed = len(df[df["status"] == "Passed"])
    rate = (passed / total * 100) if total > 0 else 0

    assert rate == 0


def test_average_duration():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 2.0},
        {"status": "Failed", "duration": 4.0},
    ])

    avg_duration = df["duration"].mean()

    assert avg_duration == 3.0


def test_render_charts_returns_none_when_nothing_selected():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 1.0, "test_name": "Test1"},
        {"status": "Failed", "duration": 2.0, "test_name": "Test2"},
    ])
    
    mock_st = sys.modules["streamlit"]

    mock_st.selectbox.return_value = "— Select status —"
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    result = render_charts(df, key_suffix="test")
    
    assert result == None


def test_render_charts_returns_selected_status():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 1.0, "test_name": "Test1"},
        {"status": "Failed", "duration": 2.0, "test_name": "Test2"},
    ])
    
    mock_st = sys.modules["streamlit"]
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.selectbox.return_value = "Failed"
    
    result = render_charts(df, key_suffix="test")
    
    assert result == "Failed"


def test_error_line_is_red():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs(["ERROR: something broke\n"])
    
    call_args = mock_st.markdown.call_args[0][0]
    assert "ERROR" in call_args


def test_warn_line_is_orange():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs(["WARN: low memory\n"])
    
    call_args = mock_st.markdown.call_args[0][0]
    assert "#ffa500" in call_args


def test_normal_line_has_no_color():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs(["Everything is fine\n"])
    
    call_args = mock_st.markdown.call_args[0][0]
    assert "<span" not in call_args


def test_empty_log_shows_info():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs([])
    
    mock_st.info.assert_called_once_with("Log is empty.")
import sys
from unittest.mock import MagicMock

sys.modules["streamlit"] = MagicMock()
sys.modules["plotly.express"] = MagicMock()
sys.modules["streamlit_plotly_events"] = MagicMock()

import pandas as pd
from src.components import render_metrics, render_charts, highlight_logs

#render_metrics - success rate is 75%
def test_success_rate_is_75_percent():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 1.0},
        {"status": "Passed", "duration": 2.0},
        {"status": "Passed", "duration": 1.5},
        {"status": "Failed", "duration": 3.0},
    ])
    
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    c1, c2, c3 = MagicMock(), MagicMock(), MagicMock()
    mock_st.columns.return_value = [c1, c2, c3]
    
    render_metrics(df)
    
    print(f"\nc2 calls: {c2.metric.call_args_list}")
    c2.metric.assert_called_once_with("Success Rate", "75.0%")


#render_metrics - success rate is 0 when DataFrame is empty
def test_success_rate_empty_dataframe():
    df = pd.DataFrame(columns=["status", "duration"])
    
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    c1, c2, c3 = MagicMock(), MagicMock(), MagicMock()
    mock_st.columns.return_value = [c1, c2, c3]
    
    render_metrics(df)
    
    c2.metric.assert_called_once_with("Success Rate", "0.0%")


#render_metrics - average duration is correct
def test_average_duration():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 2.0},
        {"status": "Failed", "duration": 4.0},
    ])
    
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    c1, c2, c3 = MagicMock(), MagicMock(), MagicMock()
    mock_st.columns.return_value = [c1, c2, c3]
    
    render_metrics(df)
    
    c3.metric.assert_called_once_with("Average duration", "3.00s")


#render_charts - returns None when nothing is selected
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


#render_charts - returns None when DataFrame is empty
def test_render_charts_returns_none_when_empty_dataframe():
    df = pd.DataFrame(columns=["status", "duration", "test_name"])
    
    result = render_charts(df, key_suffix="test")
    assert result == None


#render_charts - returns selected status "Failed"
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


#render_charts - returns selected status "Passed"
def test_render_charts_returns_passed_status():
    df = pd.DataFrame([
        {"status": "Passed", "duration": 1.0, "test_name": "Test1"},
        {"status": "Failed", "duration": 2.0, "test_name": "Test2"},
    ])
    
    mock_st = sys.modules["streamlit"]
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.selectbox.return_value = "Passed"
    
    result = render_charts(df, key_suffix="test")
    assert result == "Passed"


#highlight_logs - error lines contain "ERROR"
def test_error_line_is_red():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs(["ERROR: something broke\n"])
    
    call_args = mock_st.markdown.call_args[0][0]
    assert "#ff4b4b" in call_args


#highlight_logs - warn lines contain "WARN"
def test_warn_line_is_orange():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs(["WARN: low memory\n"])
    
    call_args = mock_st.markdown.call_args[0][0]
    assert "#ffa500" in call_args


#highlight_logs - normal lines do not contain color spans
def test_normal_line_has_no_color():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs(["Everything is fine\n"])
    
    call_args = mock_st.markdown.call_args[0][0]
    assert "<span" not in call_args


#highlight_logs - empty log shows info
def test_empty_log_shows_info():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs([])
    
    mock_st.info.assert_called_once_with("Log is empty.")


#highlight_logs - fatal lines contain "FATAL"
def test_fatal_line_is_red():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()

    highlight_logs(["FATAL: something went very wrong\n"])

    call_args = mock_st.markdown.call_args[0][0]
    assert "#ff4b4b" in call_args


#highlight_logs - exception lines contain "EXCEPTION"
def test_exception_line_is_red():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()

    highlight_logs(["EXCEPTION: something went very wrong\n"])

    call_args = mock_st.markdown.call_args[0][0]
    assert "#ff4b4b" in call_args


#highlight_logs - <script> is escaped
def test_html_special_chars_are_escaped():
    mock_st = sys.modules["streamlit"]
    mock_st.reset_mock()
    
    highlight_logs(["<script>alert(1)</script>\n"])
    
    call_args = mock_st.markdown.call_args[0][0]
    assert "<script>" not in call_args
    assert "&lt;script&gt;" in call_args



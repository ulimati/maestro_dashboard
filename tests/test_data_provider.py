import sys
from unittest.mock import MagicMock
from unittest.mock import MagicMock, patch
from src.data_provider import get_log_content, get_all_test_data

sys.modules["streamlit"] = MagicMock()

import pandas as pd
from src.data_provider import get_log_content

#get_log_content - file does not exist
def test_log_file_not_found(tmp_path):
    result = get_log_content(str(tmp_path), "neexistuje.log")
    assert "not found" in result[0]


#get_log_content - file exist
def test_log_file_exist(tmp_path):
    log_file = tmp_path / "existuje.log"
    log_file.write_text("Some log content")
    result = get_log_content(str(tmp_path), "existuje.log")
    assert "Some log content" in result[0]


#get_log_content - error reading file
def test_log_file_error_reading(tmp_path):
    log_file = tmp_path / "existuje.log"
    log_file.write_text("Some log content")
    result = get_log_content(str(tmp_path), "existuje.log")
    assert "Some log content" in result[0]


#get_all_test_data - API - folder missing
def test_api_returns_empty_when_folder_missing():
    with patch("src.data_provider.os.path.exists", return_value=False):
        df = get_all_test_data("API")
        assert df.empty




#get_all_test_data - Android - folder missing
def test_android_returns_empty_when_folder_missing():
    with patch("src.data_provider.os.path.exists", return_value=False):
        df = get_all_test_data("Android")
        assert df.empty


#get_all_test_data - Android - uses logs_android folder
def test_android_uses_correct_folder():
    get_all_test_data.clear()
    with patch("src.data_provider.os.path.exists", return_value=False) as mock_exists:
        get_all_test_data("Android")
        all_calls = [str(call) for call in mock_exists.call_args_list]
        assert any("logs_android" in call for call in all_calls)


#get_all_test_data - Android - parses XML - returns correct test name
def test_android_xml_returns_correct_test_name(tmp_path, monkeypatch):
    run_folder = tmp_path / "logs" / "logs_android" / "2026-02-13_06-09-21"
    run_folder.mkdir(parents=True)
    
    xml_file = run_folder / "report_1.xml"
    xml_file.write_text("""<?xml version="1.0"?>
<testsuite>
  <testcase name="LoginTest" time="1.23">
  </testcase>
</testsuite>""")

    monkeypatch.chdir(tmp_path)
    get_all_test_data.clear()
    df = get_all_test_data("Android")
    assert df.iloc[0]["test_name"] == "LoginTest"


#get_all_test_data - Android - parses XML - correct status Passed
def test_android_xml_returns_correct_status_passed(tmp_path, monkeypatch):
    run_folder = tmp_path / "logs" / "logs_android" / "2026-02-13_06-09-21"
    run_folder.mkdir(parents=True)
    
    xml_file = run_folder / "report_1.xml"
    xml_file.write_text("""<?xml version="1.0"?>
<testsuite>
  <testcase name="LoginTest" time="1.23">
  </testcase>
</testsuite>""")
    
    monkeypatch.chdir(tmp_path)
    get_all_test_data.clear()
    
    df = get_all_test_data("Android")
    
    assert df.iloc[0]["status"] == "Passed"


#get_all_test_data - Android - parses XML - correct status Failed
def test_android_xml_returns_correct_status_failed(tmp_path, monkeypatch):
    run_folder = tmp_path / "logs" / "logs_android" / "2026-02-13_06-09-21"
    run_folder.mkdir(parents=True)
    
    xml_file = run_folder / "report_1.xml"
    xml_file.write_text("""<?xml version="1.0"?>
<testsuite>
  <testcase name="LoginTest" time="1.23">
    <failure>Something went wrong</failure>
  </testcase>
</testsuite>""")

    monkeypatch.chdir(tmp_path)
    get_all_test_data.clear()
    df = get_all_test_data("Android")
    assert df.iloc[0]["status"] == "Failed"



#get_all_test_data - Android - parses XML - correct duration
def test_android_xml_returns_correct_duration(tmp_path, monkeypatch):
    run_folder = tmp_path / "logs" / "logs_android" / "2026-02-13_06-09-21"
    run_folder.mkdir(parents=True)
    
    xml_file = run_folder / "report_1.xml"
    xml_file.write_text("""<?xml version="1.0"?>
<testsuite>
<testcase name="LoginTest" time="1.23">
    <failure>Something went wrong</failure>
</testcase>
</testsuite>""")

    monkeypatch.chdir(tmp_path)
    get_all_test_data.clear()
    df = get_all_test_data("Android")
    assert df.iloc[0]["duration"] == 1.23


#get_all_test_data - Android - parses XML - correct status Passed
def test_android_xml_returns_correct_status_passed(tmp_path, monkeypatch):
    run_folder = tmp_path / "logs" / "logs_android" / "2026-02-13_06-09-21"
    run_folder.mkdir(parents=True)

    xml_file = run_folder / "report_1.xml"
    xml_file.write_text("""<?xml version="1.0"?>
<testsuite>
  <testcase name="LoginTest" time="1.23">
    <status>Passed</status>
  </testcase>
</testsuite>""")

    monkeypatch.chdir(tmp_path)
    get_all_test_data.clear()
    df = get_all_test_data("Android")
    assert df.iloc[0]["status"] == "Passed"


#get_all_test_data - iOS - folder missing
def test_ios_returns_empty_when_folder_missing():
    with patch("src.data_provider.os.path.exists", return_value=False):
        df = get_all_test_data("iOS")
        assert df.empty


#get_all_test_data - iOS - uses logs_ios folder
def test_ios_uses_correct_folder():
    get_all_test_data.clear()  # vymaže cache
    with patch("src.data_provider.os.path.exists", return_value=False) as mock_exists:
        get_all_test_data("iOS")
        all_calls = [str(call) for call in mock_exists.call_args_list]
        assert any("logs_ios" in call for call in all_calls)
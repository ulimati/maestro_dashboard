import sys
from unittest.mock import MagicMock

sys.modules["streamlit"] = MagicMock()

import pandas as pd
from src.data_provider import get_log_content


def test_log_file_not_found(tmp_path):
    result = get_log_content(str(tmp_path), "neexistuje.log")
    assert "not found" in result[0]
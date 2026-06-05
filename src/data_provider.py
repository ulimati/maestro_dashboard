import os
import json
import xml.etree.ElementTree as ET
import pandas as pd

# ---------------------------------------------------------------
# Pomocná funkce: načti XML testy ze složky logs_android / logs_ios
# ---------------------------------------------------------------
def get_all_test_data(platform: str) -> pd.DataFrame:
    """
    Načte testovací data ze souborů v logs/.
    platform: "Android" | "iOS" | "API" (nebo cokoliv s "API")
    """
    if "API" in platform:
        return _load_json_logs("logs/json")

    folder_map = {
        "Android": "logs/logs_android",
        "iOS":     "logs/logs_ios",
    }
    logs_dir = folder_map.get(platform, "logs/logs_android")

    rows = []
    if not os.path.exists(logs_dir):
        return pd.DataFrame()

    for run_id in sorted(os.listdir(logs_dir)):
        run_path = os.path.join(logs_dir, run_id)
        if not os.path.isdir(run_path):
            continue
        for file in os.listdir(run_path):
            if file.endswith(".xml"):
                xml_path = os.path.join(run_path, file)
                try:
                    tree = ET.parse(xml_path)
                    root = tree.getroot()
                    for testcase in root.iter("testcase"):
                        failure = testcase.find("failure")
                        status = "Failed" if failure is not None else "Passed"
                        rows.append({
                            "run_id":      run_id,
                            "test_name":   testcase.get("name"),
                            "status":      status,
                            "duration":    float(testcase.get("time", 0)),
                            "error_msg":   failure.text if failure is not None else None,
                            "folder_path": run_path,
                        })
                except Exception:
                    pass

    return pd.DataFrame(rows)


# ---------------------------------------------------------------
# Načti JSON logy pro API testy
# ---------------------------------------------------------------
def _load_json_logs(folder: str) -> pd.DataFrame:
    rows = []
    if not os.path.exists(folder):
        return pd.DataFrame()

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(folder, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for iteration in data:
                run_id = filename.replace(".json", "")
                for result in iteration.get("results", []):
                    passed = result.get("status") == "pass"
                    rows.append({
                        "run_id":    run_id,
                        "test_name": result.get("name", filename),
                        "status":    "Passed" if passed else "Failed",
                        "duration":  round(result.get("runDuration", 0), 2),
                        "error_msg": result.get("error"),
                        "folder_path": folder,
                    })
        except Exception:
            pass

    return pd.DataFrame(rows)


# ---------------------------------------------------------------
# Načti obsah log souboru (console_output.log apod.)
# ---------------------------------------------------------------
def get_log_content(folder_path: str, filename: str):
    path = os.path.join(folder_path, filename)
    if os.path.exists(path):
        with open(path, "r", errors="ignore") as f:
            return f.readlines()
    return None

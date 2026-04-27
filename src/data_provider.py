from src.db import db
import os
import xml.etree.ElementTree as ET
import pandas as pd

test_results = db["test_results"]
api_test_runs = db["api_test_runs"]

def get_metrics_for_platform(platform: str):
    platform_lower = platform.lower()
    
    # API testy jsou v jiné kolekci
    if platform_lower == "api":
        col = api_test_runs
        query = {}
        status_passed = "Passed"
        status_failed = "Failed"
    else:
        col = test_results
        query = {"platform": {"$regex": f"^{platform}$", "$options": "i"}}
        status_passed = "passed"
        status_failed = "failed"

    results = list(col.find(query))
    total  = len(results)
    passed = sum(1 for r in results if r.get("status") == status_passed)
    failed = sum(1 for r in results if r.get("status") == status_failed)

    avg_duration = sum(r.get("duration", 0) for r in results) / total if total else 0
    pass_rate    = round(passed / total * 100, 2) if total else 0

    chart_data = []
    for r in results[-50:]:
        chart_data.append({
            "name":     r.get("test_name", "Neznámý test"),
            "duration": round(r.get("duration", 0), 2),
            "status":   r.get("status", "unknown"),
            "date":     r.get("run_date").strftime("%Y-%m-%d") if r.get("run_date") else ""
        })

    return {
        "total":       total,
        "passed":      passed,
        "failed":      failed,
        "passRate":    pass_rate,
        "avgDuration": round(avg_duration, 2),
        "chartData":   chart_data,
    }

def get_all_test_data(platform: str) -> pd.DataFrame:
    if "API" in platform:
        folder = "logs/json"
        # JSON logy – vracíme prázdný DataFrame (nebo implementuj dle potřeby)
        return pd.DataFrame()
    
    folder_map = {"Android": "logs/logs_android", "iOS": "logs/logs_ios"}
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
                    for testcase in root.iter('testcase'):
                        failure = testcase.find('failure')
                        status = "Failed" if failure is not None else "Passed"
                        rows.append({
                            "run_id": run_id,
                            "test_name": testcase.get('name'),
                            "status": status,
                            "duration": float(testcase.get('time', 0)),
                            "error_msg": failure.text if failure is not None else None,
                            "folder_path": run_path,
                        })
                except:
                    pass
    
    return pd.DataFrame(rows)

def get_log_content(folder_path: str, filename: str):
    path = os.path.join(folder_path, filename)
    if os.path.exists(path):
        with open(path, 'r', errors='ignore') as f:
            return f.readlines()
    return None

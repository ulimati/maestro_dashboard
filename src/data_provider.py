import os
import pandas as pd
import xml.etree.ElementTree as ET
import json
import streamlit as st

@st.cache_data(ttl=600)
def get_all_test_data(platform_selection):
    data = []
    
    # API platform - čte z logs/json
    if "API" in platform_selection:
        json_dir = os.path.join("logs", "json")
        if not os.path.exists(json_dir):
            return pd.DataFrame()
        
        for file in os.listdir(json_dir):
            if not file.endswith(".json"):
                continue
            
            json_path = os.path.join(json_dir, file)
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                
                # JSON je list, bereme první prvek
                if isinstance(json_data, list) and len(json_data) > 0:
                    item = json_data[0]
                else:
                    continue
                
                # run_id z názvu souboru (datum+čas)
                run_id = file[:13]  # "20260217_0828"
                
                # Procházení jednotlivých výsledků testů
                for result in item.get("results", []):
                    test_name = result.get("name", file)
                    status = "Passed" if result.get("status") == "pass" else "Failed"
                    duration = round(result.get("runDuration", 0), 3)
                    
                    # Chybová zpráva z testResults
                    error_msg = ""
                    for test_result in result.get("testResults", []):
                        if test_result.get("status") == "fail":
                            error_msg = test_result.get("description", "")
                            break
                    
                    # HTTP status z response
                    response = result.get("response", {})
                    http_status = response.get("status", "")
                    
                    data.append({
                        "run_id": run_id,
                        "test_id": file.replace(".json", ""),
                        "test_name": test_name,
                        "status": status,
                        "duration": duration,
                        "error_msg": error_msg,
                        "http_status": http_status,
                        "folder_path": json_dir
                    })
            except Exception as e:
                print(f"Chyba při parsování {json_path}: {e}")
        
        return pd.DataFrame(data)
    
    # Android / iOS - čte z logs/logs_android nebo logs/logs_ios
    folder_name = "logs_android" if "Android" in platform_selection else "logs_ios"
    logs_dir = os.path.join("logs", folder_name)
    
    if not os.path.exists(logs_dir):
        return pd.DataFrame()

    for run_id in os.listdir(logs_dir):
        run_path = os.path.join(logs_dir, run_id)
        
        if os.path.isdir(run_path):
            for file in os.listdir(run_path):
                if file.endswith(".xml"):
                    xml_path = os.path.join(run_path, file)
                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        
                        for testcase in root.iter('testcase'):
                            test_name = testcase.get('name')
                            duration = float(testcase.get('time', 0))
                            test_id = file.replace("report_", "").replace(".xml", "")
                            
                            failure_node = testcase.find('failure')
                            status = "Failed" if failure_node is not None else "Passed"
                            error_msg = failure_node.text if failure_node is not None else ""

                            data.append({
                                "run_id": run_id,
                                "test_id": test_id,
                                "test_name": test_name,
                                "status": status,
                                "duration": duration,
                                "error_msg": error_msg,
                                "folder_path": run_path
                            })
                    except Exception as e:
                        print(f"Chyba při parsování {xml_path}: {e}")

    return pd.DataFrame(data)

def get_log_content(folder_path, filename):
    file_path = os.path.join(folder_path, filename)
    if not os.path.exists(file_path):
        return [f"Soubor {filename} nebyl nalezen."]
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except Exception as e:
        return [f"Chyba při čtení logu: {str(e)}"]
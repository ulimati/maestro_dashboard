import os
import pandas as pd
import xml.etree.ElementTree as ET
import json
import streamlit as st

@st.cache_data
def get_all_test_data(platform_selection):
    """
    Načte data z XML a JSON reportů na základě zvolené platformy.
    Očekává strukturu: logs/logs_android/... nebo logs/logs_ios/...
    """
    data = []
    
    # Dynamické určení složky podle ikony v radio buttonu
    folder_name = "logs_android" if "Android" in platform_selection else "logs_ios"
    logs_dir = os.path.join("logs", folder_name)
    
    if not os.path.exists(logs_dir):
        return pd.DataFrame()

    # Procházení jednotlivých běhů (složek s časovou značkou)
    for run_id in os.listdir(logs_dir):
        run_path = os.path.join(logs_dir, run_id)
        
        if os.path.isdir(run_path):
            # Procházení souborů v daném běhu
            for file in os.listdir(run_path):
                
                # --- ZPRACOVÁNÍ XML ---
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

                # --- ZPRACOVÁNÍ JSON ---
                elif file.endswith(".json"):
                    json_path = os.path.join(run_path, file)
                    try:
                        # Opraveno na json.load()
                        with open(json_path, "r", encoding="utf-8") as f:
                            json_data = json.load(f)

                            # Opraveno odstraňování přípony .json
                            test_id = file.replace("report_", "").replace(".json", "")
                            test_name = json_data.get("name", file)

                            total_tests = int(json_data.get("totalTests",0))
                            passed_tests = int(json_data.get("passedTests",0))
                            failed_tests = int(json_data.get("failedTests",0))

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
                        print(f"Chyba při parsování {json_path}: {e}") # Opraven výpis proměnné

    return pd.DataFrame(data)

def get_log_content(folder_path, filename):
    """Načte obsah logu pro detail testu."""
    file_path = os.path.join(folder_path, filename)
    if not os.path.exists(file_path):
        return [f"Soubor {filename} nebyl nalezen."]
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except Exception as e:
        return [f"Chyba při čtení logu: {str(e)}"]
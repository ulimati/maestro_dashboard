import os
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

# URL local FastAPI
API_URL = "http://localhost:8000/api/test-results"

def upload_xml_logs(folder_name, platform):
    logs_dir = os.path.join("logs", folder_name)
    if not os.path.exists(logs_dir):
        print(f"Složka {logs_dir} neexistuje, přeskakuji...")
        return

    print(f"Zpracovávám logy z {logs_dir} pro platformu: {platform}")
    for run_id in os.listdir(logs_dir):
        run_path = os.path.join(logs_dir, run_id)
        
        if os.path.isdir(run_path):
            try:
                run_date = datetime.strptime(run_id[:10], "%Y-%m-%d")
            except:
                run_date = datetime.now()

            for file in os.listdir(run_path):
                if file.endswith(".xml"):
                    xml_path = os.path.join(run_path, file)
                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        
                        for testcase in root.iter('testcase'):
                            test_name = testcase.get('name')
                            duration = float(testcase.get('time', 0))
                            
                            failure_node = testcase.find('failure')
                            status = "failed" if failure_node is not None else "passed"
                            error_msg = failure_node.text if failure_node is not None else None

                            payload = {
                                "test_name": test_name,
                                "status": status,
                                "duration": duration,
                                "platform": platform,
                                "error_message": error_msg,
                                "timestamp": run_date.isoformat()
                            }
                            
                            response = requests.post(API_URL, json=payload)
                            if response.status_code == 200:
                                print(f"✅ Nahráno: {test_name} ({platform}) [{run_date.date()}]")
                            else:
                                print(f"❌ Chyba: {response.text}")
                    except Exception as e:
                        print(f"⚠️ Chyba při parsování {xml_path}: {e}")

if __name__ == "__main__":
    upload_xml_logs("logs_android", "android")
    upload_xml_logs("logs_ios", "ios")
    print("Hotovo! Data jsou v MongoDB.")
import os
from datetime import datetime 

def log_crm_heartbeat():
    
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    tmp_dir = "/tmp" if os.name != "nt" else os.path.join(os.getcwd(), "crm", "logs")
    os.makedirs(tmp_dir, exist_ok=True)

    log_path = os.path.join(tmp_dir, "crm_heartbeat_log.txt")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_message)

    
import os
from datetime import datetime 
import requests

def log_crm_heartbeat():
    
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    tmp_dir = "/tmp" if os.name != "nt" else os.path.join(os.getcwd(), "crm", "logs")
    os.makedirs(tmp_dir, exist_ok=True)

    log_path = os.path.join(tmp_dir, "crm_heartbeat_log.txt")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_message)

    

def update_low_stock():
    """Runs every 12 hours — restocks products via GraphQL mutation."""
    mutation = """
    mutation {
      updateLowStockProducts {
        success
        message
        updatedProducts {
          name
          stock
        }
      }
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": mutation},
            timeout=10
        )
        data = response.json()
        result = data.get("data", {}).get("updateLowStockProducts", {})

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tmp_dir = "/tmp" if os.name != "nt" else os.path.join(os.getcwd(), "crm", "logs")
        os.makedirs(tmp_dir, exist_ok=True)
        log_path = os.path.join(tmp_dir, "low_stock_updates_log.txt")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{timestamp} — {result.get('message')}\n")
            for prod in result.get("updatedProducts", []):
                f.write(f"   {prod['name']}: new stock = {prod['stock']}\n")

        print("Low-stock update completed")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} — Error: {e}\n")
        print("Error updating low-stock products:", e)

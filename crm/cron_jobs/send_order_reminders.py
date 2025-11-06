#!/usr/bin/env python3
import os
from datetime import datetime
import requests

GRAPHQL_URL = "http://127.0.0.1:8000/graphql"

query = """
query {
  allOrders {
    edges {
      node {
        id
        customer {
          name
          email
        }
        totalAmount
      }
    }
  }
}
"""

# absolute path for logs
project_root = os.path.join(os.getcwd(), "crm", "cron_jobs")
os.makedirs(project_root, exist_ok=True)
log_path = os.path.join(project_root, "order_reminders_log.txt")

try:
    response = requests.post(GRAPHQL_URL, json={"query": query})
    response.raise_for_status()

    data = response.json()
    orders = data.get("data", {}).get("allOrders", {}).get("edges", [])

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{datetime.now()} - Retrieved {len(orders)} orders\n")
        for order in orders:
            node = order["node"]
            customer = node.get("customer", {}).get("name", "Unknown")
            total = node.get("totalAmount", "0.00")
            f.write(f"   - {customer}: GHS {total}\n")

    print(f"Logged {len(orders)} orders to {log_path}")

except Exception as e:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{datetime.now()} -  Error: {str(e)}\n")
    print("Error logged:", e)

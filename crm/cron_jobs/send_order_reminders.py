#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_URL = "http://localhost:8000/graphql"

today = datetime.now()
week_ago = today - timedelta(days=7)

query = gql("""
query GetRecentOrders($afterDate: DateTime!) {
  allOrders(orderDate_Gte: $afterDate) {
    edges {
      node {
        id
        customer {
          email
        }
        orderDate
      }
    }
  }
}
""")


transport = RequestsHTTPTransport(
    url=GRAPHQL_URL,
    verify=False,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=False)

project_root = os.path.join(os.getcwd(), "crm", "cron_jobs")
os.makedirs(project_root, exist_ok=True)
log_path = os.path.join(project_root, "order_reminders_log.txt")

try:
    variables = {"afterDate": week_ago.isoformat()}
    response = client.execute(query, variable_values=variables)

    orders = response.get("allOrders", {}).get("edges", [])

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{datetime.now()} - Found {len(orders)} orders in the last week\n")
        for order in orders:
            node = order["node"]
            order_id = node["id"]
            email = node["customer"]["email"]
            f.write(f"   - Order ID: {order_id}, Email: {email}\n")

    print("Order reminders processed!")

except Exception as e:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{datetime.now()} - Error: {e}\n")
    print("Error occurred while processing order reminders:", e)

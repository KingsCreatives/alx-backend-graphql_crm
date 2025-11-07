from celery import shared_task
import os
import requests
from datetime import datetime

@shared_task
def generate_crm_report():
    """
    Fetch total customers, orders, and revenue using GraphQL
    and log results to /tmp/crm_report_log.txt
    """
    query = """
    {
      allCustomers {
        totalCount
      }
      allOrders {
        totalCount
        edges {
          node {
            totalAmount
          }
        }
      }
    }
    """

    try:
        response = requests.post("http://localhost:8000/graphql", json={"query": query})
        data = response.json()["data"]

        total_customers = data["allCustomers"]["totalCount"]
        total_orders = data["allOrders"]["totalCount"]

        total_revenue = sum(
            float(order["node"]["totalAmount"]) for order in data["allOrders"]["edges"]
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, GHS {total_revenue:.2f} revenue\n"
        )

        tmp_dir = "/tmp" if os.name != "nt" else os.path.join(os.getcwd(), "crm", "logs")
        os.makedirs(tmp_dir, exist_ok=True)
        log_path = os.path.join(tmp_dir, "crm_report_log.txt")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(report)

        print("Weekly CRM report generated successfully!")

    except Exception as e:
        print(f"Error generating CRM report: {e}")

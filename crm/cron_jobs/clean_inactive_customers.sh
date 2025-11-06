#!/bin/bash

cd "$(dirname "$0")/../.."

python manage.py shell <<'EOF'
import os
from datetime import timedelta, datetime
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)

inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago)
deleted_count = inactive_customers.count()
inactive_customers.delete()

# stable absolute path for the log
project_root = os.path.join(os.getcwd(), "crm", "cron_jobs")
os.makedirs(project_root, exist_ok=True)
log_path = os.path.join(project_root, "customer_cleanup_log.txt")

# Write to log file
with open(log_path, "a", encoding="utf-8") as f:
    f.write(f"{datetime.now()} - Deleted {deleted_count} inactive customers\n")

print("Logged cleanup results to:", log_path)
EOF

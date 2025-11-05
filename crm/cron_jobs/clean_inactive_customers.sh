#!/bin/bash

cd "$(dirname "$0")/../.."

python manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago)

deleted_count = inactive_customers.count()
inactive_customers.delete()

# Log the result with timestamp
with open("/tmp/customer_cleanup_log.txt", "a") as f:
    from datetime import datetime
    f.write(f"{datetime.now()} - Deleted {deleted_count} inactive customers\n")
EOF

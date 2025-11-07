## Celery Task for Weekly CRM Report

---

This task configures **Celery** and **Celery Beat** to automatically generate a **weekly CRM summary report** every **Monday at 6 AM**.
The report summarizes:

- Total number of customers
- Total number of orders
- Total revenue

Each run logs the results to **`/tmp/crm_report_log.txt`**.

---

### ⚙️ 1. Install Redis and Dependencies

**Install Redis:**

```bash
sudo apt update
sudo apt install redis-server -y
```

**Start Redis:**

```bash
sudo service redis-server start
```

**Install Python Dependencies:**

```bash
pip install celery django-celery-beat redis
```

Make sure these are added to your `requirements.txt`:

```
celery
django-celery-beat
redis
```

---

### 🛠️ 2. Run Migrations

```bash
python3 manage.py migrate
```

This will apply database tables for **django-celery-beat** and any pending migrations in your CRM app.

---

### 🚀 3. Start Celery Worker

From the **project root**, run:

```bash
celery -A crm worker -l info
```

The worker is responsible for **executing** scheduled Celery tasks.

Expected output (snippet):

```
[tasks]
  . crm.tasks.generate_crm_report
```

---

### ⏱️ 4. Start Celery Beat

In a **separate terminal**, run:

```bash
celery -A crm beat -l info
```

Celery Beat is the **scheduler** that triggers your periodic tasks (like the Monday 6 AM report).

Expected output:

```
[INFO/MainProcess] beat: Starting...
[INFO/MainProcess] Scheduler: Sending due task generate-crm-report (crm.tasks.generate_crm_report)
```

---

### 🧪 5. Verify Logs

To confirm the task executed successfully:

```bash
cat /tmp/crm_report_log.txt
```

Example output:

```
2025-11-07 06:00:00 - Report: 12 customers, 34 orders, GHS 7420.00 revenue
```

---

### **Summary**

| Step | Command                           | Purpose              |
| ---- | --------------------------------- | -------------------- |
| 1    | `sudo service redis-server start` | Start Redis broker   |
| 2    | `python3 manage.py migrate`       | Apply migrations     |
| 3    | `celery -A crm worker -l info`    | Start task executor  |
| 4    | `celery -A crm beat -l info`      | Start task scheduler |
| 5    | `cat /tmp/crm_report_log.txt`     | Verify log output    |

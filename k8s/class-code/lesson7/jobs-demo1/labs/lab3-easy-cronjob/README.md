# Lab 3: Easy CronJob - Daily Log Cleanup

## Objective

Create a Kubernetes CronJob that runs daily to clean up old log files.

## Requirements

- CronJob should run every day at 2:00 AM
- Find and delete log files older than 7 days
- Log the cleanup operation
- Use a simple schedule expression
- Handle the case when no files are found

## Tasks

1. Create a Python script (`cleanup-logs.py`) or Bash script (`cleanup-logs.sh`)
2. Create a Dockerfile
3. Create a Kubernetes CronJob YAML file with:
   - Schedule: `0 2 * * *` (2 AM daily)
   - SuccessfulJobsHistoryLimit and FailedJobsHistoryLimit
4. Apply the CronJob
5. Manually trigger it to test: `kubectl create job --from=cronjob/log-cleanup-cronjob manual-test`
6. Monitor the execution

## Schedule Format

Cron format: `minute hour day month weekday`

- `0 2 * * *` = Every day at 2:00 AM
- `*/5 * * * *` = Every 5 minutes
- `0 0 * * 0` = Every Sunday at midnight

## Expected Output

```
[2024-01-15 02:00:00] Starting log cleanup job...
Scanning for log files older than 7 days...
Found 5 log files to delete
Deleted: /tmp/logs/app-2024-01-01.log
Deleted: /tmp/logs/app-2024-01-02.log
...
Cleanup completed: 5 files deleted
Job completed successfully!
```

## Solution Steps

1. Build image: `docker build -t log-cleanup:latest -f Dockerfile .`
2. Apply cronjob: `kubectl apply -f cronjob.yaml`
3. Check cronjob: `kubectl get cronjobs`
4. Manually trigger: `kubectl create job --from=cronjob/log-cleanup-cronjob manual-test`
5. View logs: `kubectl logs job/manual-test`
6. Check schedule: `kubectl get cronjob log-cleanup-cronjob -o yaml`

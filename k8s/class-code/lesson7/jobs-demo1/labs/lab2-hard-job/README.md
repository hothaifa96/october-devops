# Lab 2: Hard Job - Database Backup with Retry Logic

## Objective
Create a Kubernetes Job that simulates a database backup operation with:
- Retry logic for transient failures
- Error handling and validation
- Progress reporting
- Configurable retry attempts and delays
- Proper exit codes

## Requirements
- Job should retry up to 3 times on failure
- Simulate backup operation (create backup file)
- Validate backup file exists and has content
- Use environment variables for configuration
- Handle errors gracefully
- Set resource limits

## Tasks
1. Create a Python script (`backup-db.py`) or Bash script (`backup-db.sh`)
2. Implement retry logic with exponential backoff
3. Create a Dockerfile
4. Create a Kubernetes Job YAML with:
   - Environment variables
   - Resource limits
   - Backoff limit configuration
5. Test with intentional failures
6. Verify retry behavior

## Configuration
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `RETRY_DELAY`: Initial delay between retries in seconds (default: 2)
- `BACKUP_PATH`: Path where backup file will be created
- `FAIL_RATE`: Probability of failure (0.0-1.0) for testing

## Expected Behavior
- Job should retry on failures
- After successful backup, validate the file
- Exit with code 0 on success, 1 on failure
- Log all retry attempts

## Solution Steps
1. Build image: `docker build -t db-backup:latest -f Dockerfile .`
2. Apply job: `kubectl apply -f job.yaml`
3. Monitor: `kubectl get jobs -w`
4. Check logs: `kubectl logs job/db-backup-job`
5. Test failure: Set `FAIL_RATE=0.8` to test retries


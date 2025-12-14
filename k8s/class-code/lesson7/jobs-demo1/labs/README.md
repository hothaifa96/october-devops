# Kubernetes Jobs and CronJobs - Lab Exercises

This directory contains 4 hands-on labs for learning Kubernetes Jobs and CronJobs, progressing from easy to hard.

## Lab Overview

| Lab                          | Type    | Difficulty | Description                                                |
| ---------------------------- | ------- | ---------- | ---------------------------------------------------------- |
| [Lab 1](./lab1-easy-job)     | Job     | Easy       | Simple data processing - calculate statistics from numbers |
| [Lab 2](./lab2-hard-job)     | Job     | Hard       | Database backup with retry logic and error handling        |
| [Lab 3](./lab3-easy-cronjob) | CronJob | Easy       | Daily log cleanup scheduled task                           |
| [Lab 4](./lab4-hard-cronjob) | CronJob | Hard       | Multi-step data pipeline with dependencies                 |

## Prerequisites

- Kubernetes cluster (local or remote)
- `kubectl` configured to access your cluster
- Docker installed (for building images)
- Basic understanding of YAML and containerization

## Lab Structure

Each lab contains:

- **README.md**: Detailed instructions and objectives
- **python/**: Python implementation
  - Script file (`.py`)
  - Dockerfile
  - Kubernetes YAML (`.yaml`)
- **bash/**: Bash implementation
  - Script file (`.sh`)
  - Dockerfile
  - Kubernetes YAML (`.yaml`)

## Quick Start

### For Python Labs:

```bash
cd lab1-easy-job/python
docker build -t number-processor:latest -f Dockerfile .
kubectl apply -f job.yaml
kubectl logs -f job/number-processor-job
```

### For Bash Labs:

```bash
cd lab1-easy-job/bash
docker build -t number-processor:latest -f Dockerfile .
kubectl apply -f job.yaml
kubectl logs -f job/number-processor-job
```

## Learning Objectives

### Jobs (Labs 1-2)

- Understand when to use Jobs vs Deployments
- Configure Job completion and retry policies
- Handle job failures and backoff limits
- Set resource limits for jobs
- Clean up completed jobs

### CronJobs (Labs 3-4)

- Schedule recurring tasks using cron syntax
- Configure concurrency policies
- Manage job history limits
- Handle long-running scheduled tasks
- Test CronJobs manually

## Common Commands

### Jobs

```bash
# Create a job
kubectl apply -f job.yaml

# List jobs
kubectl get jobs

# View job details
kubectl describe job <job-name>

# View logs
kubectl logs job/<job-name>

# Delete a job
kubectl delete job <job-name>

# Watch job status
kubectl get jobs -w
```

### CronJobs

```bash
# Create a cronjob
kubectl apply -f cronjob.yaml

# List cronjobs
kubectl get cronjobs

# View cronjob details
kubectl describe cronjob <cronjob-name>

# Manually trigger a cronjob
kubectl create job --from=cronjob/<cronjob-name> manual-test

# View logs of triggered job
kubectl logs job/manual-test

# Suspend a cronjob
kubectl patch cronjob <cronjob-name> -p '{"spec":{"suspend":true}}'

# Resume a cronjob
kubectl patch cronjob <cronjob-name> -p '{"spec":{"suspend":false}}'

# Delete a cronjob
kubectl delete cronjob <cronjob-name>
```

## Cron Schedule Format

Cron format: `minute hour day month weekday`

Examples:

- `0 2 * * *` - Every day at 2:00 AM
- `*/5 * * * *` - Every 5 minutes
- `0 0 * * 0` - Every Sunday at midnight
- `0 9-17 * * 1-5` - Every hour from 9 AM to 5 PM, Monday to Friday
- `0 0 1 * *` - First day of every month at midnight

## Tips for Students

1. **Start with Lab 1**: Even if you're experienced, Lab 1 helps you understand the structure
2. **Read the README**: Each lab has specific requirements and expected outputs
3. **Test manually**: Use `kubectl create job --from=cronjob/...` to test CronJobs immediately
4. **Check logs**: Always check logs to understand what's happening
5. **Clean up**: Delete jobs after testing to avoid clutter
6. **Experiment**: Try modifying schedules, retry limits, and resource constraints

## Troubleshooting

### Job not starting

- Check pod status: `kubectl get pods`
- Check events: `kubectl describe job <job-name>`
- Verify image exists: `docker images`

### CronJob not running

- Check cronjob status: `kubectl get cronjob`
- Verify schedule syntax
- Check if suspended: `kubectl get cronjob <name> -o yaml | grep suspend`
- Manually trigger to test: `kubectl create job --from=cronjob/<name> test`

### Image pull errors

- Use `imagePullPolicy: Never` for local images
- Or push images to a registry and use `imagePullPolicy: Always`

## Next Steps

After completing these labs, you should be able to:

- ✅ Create and manage Kubernetes Jobs
- ✅ Configure CronJobs for scheduled tasks
- ✅ Handle errors and retries in jobs
- ✅ Set appropriate resource limits
- ✅ Debug job failures
- ✅ Design multi-stage pipelines as CronJobs

## Additional Resources

- [Kubernetes Jobs Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [Kubernetes CronJobs Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Cron Expression Generator](https://crontab.guru/)


# Kubernetes Jobs and CronJobs

Batch and scheduled workloads are a core part of many platforms—from running ETL pipelines to nightly report generation. Kubernetes offers two purpose-built abstractions to cover those needs:

- **Jobs**: Run one-off or finite batch workloads reliably.
- **CronJobs**: Schedule Jobs to run on a recurring cadence, similar to traditional `cron`.

This tutorial walks through concepts, configuration patterns, and operational practices for both resources.

---

## Prerequisites

- Access to a Kubernetes cluster v1.21 or later (Minikube, kind, or a managed service).
- `kubectl` installed and configured to speak to the cluster.
- Familiarity with basic Pod and Deployment concepts.

---

## Jobs Primer

Jobs ensure that a specified number of Pods successfully complete. Under the hood, a Job creates Pods and tracks completion. If a Pod fails, the Job controller creates replacement Pods until the success criteria are met or restart limits are exceeded.

### Core Properties

- `spec.template`: Pod template defining the workload (image, command, resources).
- `spec.completions`: Total successful Pod runs required (default: 1).
- `spec.parallelism`: Maximum Pods running simultaneously.
- `spec.backoffLimit`: Number of retries for failed Pods (default: 6).
- `spec.activeDeadlineSeconds`: Overall runtime limit for the Job.

### Minimal Job Example

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: hello-job
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: hello
          image: busybox:1.36
          command: ["sh", "-c", "echo 'Hello from a Job!' && sleep 2"]
```

> `restartPolicy` must be `Never` or `OnFailure` for Jobs.

### Deploying and Observing

```bash
kubectl apply -f hello-job.yaml
kubectl get jobs
kubectl get pods --selector=job-name=hello-job
kubectl logs job/hello-job
```

### Completion vs. Parallelism

- `completions`: Total number of successful Pod executions required.
- `parallelism`: Number of Pods running at once.

Example: 5 completions with parallelism 2 results in 5 total runs, with at most 2 Pods running concurrently.

```yaml
spec:
  completions: 5
  parallelism: 2
```

---

## Handling Failures

### Backoff and Retries

`backoffLimit` caps retries. A value of 0 disables retries.

```yaml
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
```

### Active Deadline

Use `activeDeadlineSeconds` to avoid runaway Jobs.

```yaml
spec:
  activeDeadlineSeconds: 120
```

### Pod Failure Diagnostics

```bash
kubectl describe job failing-job
kubectl get pods --selector=job-name=failing-job
kubectl logs failing-job-<suffix>
```

---

## Advanced Patterns

### Indexed Jobs

Indexed Jobs expose an ordinal index to each Pod via the `JOB_COMPLETION_INDEX` environment variable—useful for partitioned work.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: indexed-job
spec:
  completions: 4
  completionMode: Indexed
  parallelism: 2
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: worker
          image: alpine:3.20
          env:
            - name: JOB_COMPLETION_INDEX
              valueFrom:
                fieldRef:
                  fieldPath: metadata.annotations['batch.kubernetes.io/job-completion-index']
          command: ["sh", "-c", "echo Running shard ${JOB_COMPLETION_INDEX}"]
```

### Array Jobs via Command Arguments

Sometimes it is simpler to pass arguments directly:

```yaml
command:
  - "python"
  - "process.py"
  - "--shard=$(JOB_COMPLETION_INDEX)"
```

---

## CronJobs Primer

CronJobs schedule Jobs using a familiar cron syntax. Each schedule invocation spawns a Job object, inheriting Job behaviors.

### Core Properties

- `spec.schedule`: Cron expression (five fields: minute, hour, day of month, month, day of week).
- `spec.jobTemplate`: Job spec defining the Pod template.
- `spec.concurrencyPolicy`: Controls overlapping runs (`Allow`, `Forbid`, `Replace`).
- `spec.failedJobsHistoryLimit` / `spec.successfulJobsHistoryLimit`: Retained history.
- `spec.startingDeadlineSeconds`: Grace period to start a missed run.

### Minimal CronJob Example

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello-cron
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: hello
              image: busybox:1.36
              args:
                - /bin/sh
                - -c
                - date; echo "Hello from CronJob"
```

### Deploying and Observing

```bash
kubectl apply -f hello-cron.yaml
kubectl get cronjobs
kubectl get jobs --selector=cronjob-name=hello-cron
kubectl get pods --selector=job-name
```

Stop scheduling with:

```bash
kubectl delete cronjob hello-cron
```

---

## Scheduling Nuances

### Cron Syntax Refresher

```
┌──────── minute (0-59)
│ ┌────── hour (0-23)
│ │ ┌──── day of month (1-31)
│ │ │ ┌── month (1-12 or names)
│ │ │ │ ┌ day of week (0-6 or names; 0/7 = Sunday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

Examples:

- `0 0 * * *` — Midnight daily.
- `*/10 * * * *` — Every 10 minutes.
- `30 9 * * 1-5` — 09:30 Monday through Friday.

### concurrencyPolicy

- `Allow`: Default; overlapping runs allowed.
- `Forbid`: Skip new run if prior still active.
- `Replace`: Kill the running Job, start new one.

### Missed Runs and startingDeadlineSeconds

If the CronJob controller misses a schedule (cluster downtime, etc.), `startingDeadlineSeconds` limits how long after the scheduled time a run is still valid.

```yaml
spec:
  startingDeadlineSeconds: 300
```

### Suspend Scheduling

```bash
kubectl patch cronjob hello-cron -p '{"spec":{"suspend":true}}'
```

Set `suspend: false` to resume.

---

## Practical Example: Nightly Database Backup

### Job Template

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-backup
spec:
  backoffLimit: 2
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: backup
          image: ghcr.io/example/db-backup:1.0.0
          envFrom:
            - secretRef:
                name: backup-credentials
          args:
            - /app/backup.sh
            - "--target=s3://data-backups/prod"
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
```

### CronJob Scheduler

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-db-backup
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  failedJobsHistoryLimit: 2
  successfulJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: ghcr.io/example/db-backup:1.0.0
              envFrom:
                - secretRef:
                    name: backup-credentials
              args:
                - /app/backup.sh
                - "--target=s3://data-backups/prod"
              resources:
                requests:
                  cpu: "200m"
                  memory: "256Mi"
                limits:
                  cpu: "1"
                  memory: "1Gi"
```

---

## Managing History and Cleanup

CronJobs leave Job and Pod resources behind. Use history limits or automation to prune old runs.

```yaml
spec:
  successfulJobsHistoryLimit: 1
  failedJobsHistoryLimit: 1
```

Manual cleanup:

```bash
kubectl delete job --selector=cronjob-name=hello-cron
kubectl delete pod --selector=job-name=hello-cron-*
```

---

## Observability and Monitoring

- **Events**: `kubectl describe job/cronjob` for status messages.
- **Logs**: `kubectl logs job/<job-name>` or specific Pods.
- **Metrics**: Scrape metrics from the `kube-controller-manager` (`cronjob_controller_successful_job_creation_total`, etc.).
- **Alerting**: Instrument alerts for Jobs stuck in `Active`, repeated failures, or high retry counts.

---

## Security Considerations

- **Service Accounts**: Assign least-privilege `serviceAccountName`.
- **Secrets**: Mount credentials using Secrets or external stores.
- **Image Security**: Pin tags, enable image scanning, enforce admission policies.
- **Network**: Use NetworkPolicies to restrict outbound access when possible.

---

## Troubleshooting Checklist

1. Confirm the Job/CronJob object exists (`kubectl get`).
2. Inspect Job status conditions (`kubectl describe job`).
3. Check Pod events and container logs; identify crash loops.
4. Validate `concurrencyPolicy` isn't blocking new runs.
5. Ensure the Cron expression is correct (`crontab.guru` is handy).
6. Look for cluster-level issues—resource quotas, node pressure, controller errors.

---

## Cleanup

```bash
kubectl delete job hello-job indexed-job db-backup
kubectl delete cronjob hello-cron nightly-db-backup
```

---

## Further Reading

- [Kubernetes Documentation: Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [Kubernetes Documentation: CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Kubernetes API Reference: batch/v1](https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/job-v1/)
- [Kubebuilder Patterns for Controllers](https://kubebuilder.io/)

---

You now have the foundational patterns to run one-time and scheduled workloads on Kubernetes. Combine these primitives with observability, security, and automation best practices to build reliable batch pipelines.

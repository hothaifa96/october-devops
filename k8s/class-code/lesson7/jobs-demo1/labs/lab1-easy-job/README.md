# Lab 1: Simple Data Processing

## Requirements

- Create a Job that runs once
- Process a list of numbers (1-100)
- Calculate: sum, average, min, max
- Print results to stdout
- Job should complete successfully

## Tasks

1. Create a Python script (`process-numbers.py`) or Bash script (`process-numbers.sh`)
2. Create a Dockerfile to build the image
3. Create a Kubernetes Job YAML file
4. Build the Docker image
5. Apply the Job to your cluster
6. Check the Job status and logs

## Expected Output

```
Processing numbers from 1 to 100...
Sum: 5050
Average: 50.5
Min: 1
Max: 100
Job completed successfully!
```

## Solution Steps

1. Build image: `docker build -t number-processor:latest -f Dockerfile .`
2. Apply job: `kubectl apply -f job.yaml`
3. Check status: `kubectl get jobs`
4. View logs: `kubectl logs job/number-processor-job`
5. Clean up: `kubectl delete job number-processor-job`

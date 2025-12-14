# Lab 4: Hard CronJob - Multi-Step Data Pipeline

## Objective

Create a Kubernetes CronJob that runs a complex data pipeline with multiple steps:

1. Data extraction from multiple sources
2. Data transformation and validation
3. Data aggregation
4. Report generation
5. Cleanup of temporary files

## Requirements

- CronJob should run every hour
- Implement multiple pipeline stages
- Handle dependencies between stages
- Validate data at each stage
- Generate a summary report
- Use ConfigMaps or environment variables for configuration
- Implement proper error handling and logging
- Use concurrencyPolicy to prevent overlapping runs

## Tasks

1. Create a Python script (`data-pipeline.py`) or Bash script (`data-pipeline.sh`)
2. Implement pipeline stages:
   - Stage 1: Extract data from multiple sources
   - Stage 2: Transform and validate data
   - Stage 3: Aggregate data
   - Stage 4: Generate report
   - Stage 5: Cleanup
3. Create a Dockerfile
4. Create a Kubernetes CronJob YAML with:
   - Schedule: `0 * * * *` (every hour)
   - concurrencyPolicy: Forbid (prevent overlapping runs)
   - Resource limits
   - Environment variables for configuration
5. Test the pipeline
6. Monitor execution and verify all stages complete

## Pipeline Stages

1. **Extract**: Simulate fetching data from 3 different sources
2. **Transform**: Process and validate each data source
3. **Aggregate**: Combine all data sources
4. **Report**: Generate summary report with statistics
5. **Cleanup**: Remove temporary files

## Configuration

- `DATA_SOURCES`: Number of data sources (default: 3)
- `OUTPUT_DIR`: Directory for reports (default: /tmp/reports)
- `TEMP_DIR`: Directory for temporary files (default: /tmp/pipeline)
- `REPORT_FORMAT`: Format of report (json/text)

## Expected Output

```
[2024-01-15 10:00:00] Starting data pipeline...
=== Stage 1: Data Extraction ===
Extracting from source 1/3...
Extracting from source 2/3...
Extracting from source 3/3...
✓ Extraction completed: 3 sources

=== Stage 2: Data Transformation ===
Transforming source 1...
Transforming source 2...
Transforming source 3...
✓ Transformation completed: 3 sources validated

=== Stage 3: Data Aggregation ===
Aggregating data...
✓ Aggregation completed: 150 records

=== Stage 4: Report Generation ===
Generating report...
✓ Report generated: /tmp/reports/report-2024-01-15-10-00-00.json

=== Stage 5: Cleanup ===
Cleaning temporary files...
✓ Cleanup completed: 3 files removed

Pipeline completed successfully!
```

## Solution Steps

1. Build image: `docker build -t data-pipeline:latest -f Dockerfile .`
2. Apply cronjob: `kubectl apply -f cronjob.yaml`
3. Check cronjob: `kubectl get cronjobs`
4. Manually trigger: `kubectl create job --from=cronjob/data-pipeline-cronjob manual-run`
5. Monitor: `kubectl get jobs -w`
6. View logs: `kubectl logs job/manual-run`
7. Check concurrency: Verify only one job runs at a time

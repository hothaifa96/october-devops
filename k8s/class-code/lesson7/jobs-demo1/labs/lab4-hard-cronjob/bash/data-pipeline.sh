#!/bin/bash
# Lab 4: Hard CronJob - Multi-Step Data Pipeline
# Implements a complex data pipeline with multiple stages

set -e

# Configuration from environment variables
DATA_SOURCES=${DATA_SOURCES:-3}
OUTPUT_DIR=${OUTPUT_DIR:-/tmp/reports}
TEMP_DIR=${TEMP_DIR:-/tmp/pipeline}
REPORT_FORMAT=${REPORT_FORMAT:-json}

# Function to setup directories
setup_directories() {
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$TEMP_DIR"
    echo "✓ Directories created"
}

# Stage 1: Extract data from multiple sources
stage1_extract() {
    echo ""
    echo "=================================================="
    echo "=== Stage 1: Data Extraction ==="
    echo "=================================================="
    
    for i in $(seq 1 $DATA_SOURCES); do
        echo "Extracting from source $i/$DATA_SOURCES..."
        sleep 0.5
        
        # Simulate data extraction - create JSON file
        # Generate records array
        records="["
        for j in $(seq 1 50); do
            value=$((j * i))
            records="${records}{\"id\":$j,\"value\":$value}"
            if [ $j -lt 50 ]; then
                records="${records},"
            fi
        done
        records="${records}]"
        
        cat > "$TEMP_DIR/source_${i}_raw.json" << EOF
{
  "source_id": "source_$i",
  "records": $records,
  "extracted_at": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
  "record_count": 50
}
EOF
        
        echo "  ✓ Source $i: 50 records extracted"
    done
    
    echo ""
    echo "✓ Extraction completed: $DATA_SOURCES sources"
}

# Stage 2: Transform and validate data
stage2_transform() {
    echo ""
    echo "=================================================="
    echo "=== Stage 2: Data Transformation ==="
    echo "=================================================="
    
    for i in $(seq 1 $DATA_SOURCES); do
        echo "Transforming source $i..."
        sleep 0.3
        
        # Read source data and transform
        source_file="$TEMP_DIR/source_${i}_raw.json"
        
        if [ ! -f "$source_file" ]; then
            echo "  ✗ Error: Source file not found: $source_file"
            return 1
        fi
        
        # Calculate total and average (using jq if available, otherwise basic parsing)
        if command -v jq &> /dev/null; then
            total_value=$(jq '[.records[].value] | add' "$source_file")
            record_count=$(jq '.records | length' "$source_file")
            avg_value=$(echo "scale=2; $total_value / $record_count" | bc)
        else
            # Fallback: simple calculation
            total_value=$((i * 50 * 51 / 2))
            record_count=50
            avg_value=$(echo "scale=2; $total_value / $record_count" | bc)
        fi
        
        # Create transformed file
        cat > "$TEMP_DIR/source_${i}_transformed.json" << EOF
{
  "source_id": "source_$i",
  "transformed_at": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
  "total_value": $total_value,
  "avg_value": $avg_value,
  "record_count": $record_count
}
EOF
        
        echo "  ✓ Source $i: Validated and transformed (avg: $avg_value)"
    done
    
    echo ""
    echo "✓ Transformation completed: $DATA_SOURCES sources validated"
}

# Stage 3: Aggregate data
stage3_aggregate() {
    echo ""
    echo "=================================================="
    echo "=== Stage 3: Data Aggregation ==="
    echo "=================================================="
    
    echo "Aggregating data..."
    sleep 0.5
    
    total_records=0
    total_value=0
    
    for i in $(seq 1 $DATA_SOURCES); do
        transformed_file="$TEMP_DIR/source_${i}_transformed.json"
        if [ -f "$transformed_file" ]; then
            if command -v jq &> /dev/null; then
                records=$(jq '.record_count' "$transformed_file")
                value=$(jq '.total_value' "$transformed_file")
                total_records=$((total_records + records))
                total_value=$((total_value + value))
            else
                total_records=$((total_records + 50))
                total_value=$((total_value + i * 50 * 51 / 2))
            fi
        fi
    done
    
    avg_value=$(echo "scale=2; $total_value / $total_records" | bc)
    
    # Save aggregated data
    cat > "$TEMP_DIR/aggregated.json" << EOF
{
  "aggregated_at": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
  "total_sources": $DATA_SOURCES,
  "total_records": $total_records,
  "total_value": $total_value,
  "avg_value": $avg_value
}
EOF
    
    echo "✓ Aggregation completed: $total_records records"
    echo "$total_records|$total_value|$avg_value"
}

# Stage 4: Generate report
stage4_report() {
    local total_records=$1
    local total_value=$2
    local avg_value=$3
    
    echo ""
    echo "=================================================="
    echo "=== Stage 4: Report Generation ==="
    echo "=================================================="
    
    echo "Generating report..."
    sleep 0.3
    
    timestamp=$(date +%Y-%m-%d-%H-%M-%S)
    
    if [ "$REPORT_FORMAT" = "json" ]; then
        report_file="$OUTPUT_DIR/report-${timestamp}.json"
        cat > "$report_file" << EOF
{
  "pipeline_run": {
    "started_at": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
    "completed_at": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
    "stages_completed": 4,
    "status": "success"
  },
  "summary": {
    "total_sources": $DATA_SOURCES,
    "total_records": $total_records,
    "total_value": $total_value,
    "avg_value": $avg_value
  }
}
EOF
    else
        report_file="$OUTPUT_DIR/report-${timestamp}.txt"
        cat > "$report_file" << EOF
==================================================
Data Pipeline Report
==================================================
Generated: $(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)

Summary:
  Total Sources: $DATA_SOURCES
  Total Records: $total_records
  Total Value: $total_value
  Average Value: $avg_value
EOF
    fi
    
    echo "✓ Report generated: $report_file"
}

# Stage 5: Cleanup
stage5_cleanup() {
    echo ""
    echo "=================================================="
    echo "=== Stage 5: Cleanup ==="
    echo "=================================================="
    
    echo "Cleaning temporary files..."
    
    deleted_count=0
    for file in "$TEMP_DIR"/*.json; do
        if [ -f "$file" ]; then
            rm -f "$file"
            deleted_count=$((deleted_count + 1))
        fi
    done
    
    echo "✓ Cleanup completed: $deleted_count files removed"
}

# Main execution
main() {
    echo "=================================================="
    echo "Data Pipeline"
    echo "Started at: $(date)"
    echo "Pod Name: ${HOSTNAME:-unknown}"
    echo "=================================================="
    
    setup_directories
    stage1_extract
    stage2_transform
    
    aggregation_result=$(stage3_aggregate)
    total_records=$(echo "$aggregation_result" | cut -d'|' -f1)
    total_value=$(echo "$aggregation_result" | cut -d'|' -f2)
    avg_value=$(echo "$aggregation_result" | cut -d'|' -f3)
    
    stage4_report "$total_records" "$total_value" "$avg_value"
    stage5_cleanup
    
    echo ""
    echo "=================================================="
    echo "Pipeline completed successfully!"
    echo "Completed at: $(date)"
    echo "=================================================="
    
    exit 0
}

# Run main function
main


#!/bin/bash
# Lab 2: Hard Job - Database Backup with Retry Logic
# Simulates database backup with retry mechanism and error handling

set -e

# Configuration from environment variables
MAX_RETRIES=${MAX_RETRIES:-3}
RETRY_DELAY=${RETRY_DELAY:-2}
BACKUP_PATH=${BACKUP_PATH:-/tmp/db_backup.sql}
FAIL_RATE=${FAIL_RATE:-0.2}

# Function to simulate backup operation
simulate_backup() {
    local backup_path=$1
    echo "Attempting to create backup at: $backup_path"
    
    # Simulate potential failure (using random number)
    local random_val=$(awk "BEGIN {print rand()}")
    local fail_threshold=$(awk "BEGIN {print $FAIL_RATE}")
    
    if (( $(echo "$random_val < $fail_threshold" | bc -l) )); then
        echo "Simulated database connection timeout - transient error"
        return 1
    fi
    
    # Simulate backup operation
    sleep 1
    
    # Create backup directory if needed
    mkdir -p "$(dirname "$backup_path")"
    
    # Write mock backup data
    cat > "$backup_path" << EOF
-- Database Backup
-- Created: $(date)
-- Records: 1000
EOF
    
    echo "✓ Backup file created successfully"
    return 0
}

# Function to validate backup
validate_backup() {
    local backup_path=$1
    
    if [ ! -f "$backup_path" ]; then
        echo "Backup file not found: $backup_path"
        return 1
    fi
    
    if [ ! -s "$backup_path" ]; then
        echo "Backup file is empty: $backup_path"
        return 1
    fi
    
    local file_size=$(stat -f%z "$backup_path" 2>/dev/null || stat -c%s "$backup_path" 2>/dev/null)
    echo "✓ Backup validation passed (size: $file_size bytes)"
    return 0
}

# Function to perform backup with retry logic
perform_backup_with_retry() {
    local backup_path=$1
    local max_retries=$2
    local retry_delay=$3
    local attempt=1
    local wait_time=$retry_delay
    
    while [ $attempt -le $max_retries ]; do
        echo ""
        echo "--- Attempt $attempt/$max_retries ---"
        
        if simulate_backup "$backup_path"; then
            if validate_backup "$backup_path"; then
                echo ""
                echo "✓ Backup completed successfully on attempt $attempt"
                return 0
            fi
        fi
        
        echo "✗ Attempt $attempt failed"
        
        if [ $attempt -lt $max_retries ]; then
            wait_time=$((retry_delay * (2 ** (attempt - 1))))  # Exponential backoff
            echo "  Waiting $wait_time seconds before retry..."
            sleep $wait_time
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo ""
    echo "✗ All $max_retries attempts failed"
    return 1
}

# Main execution
echo "=================================================="
echo "Database Backup Job"
echo "Started at: $(date)"
echo "Pod Name: ${HOSTNAME:-unknown}"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  MAX_RETRIES: $MAX_RETRIES"
echo "  RETRY_DELAY: ${RETRY_DELAY}s"
echo "  BACKUP_PATH: $BACKUP_PATH"
echo "  FAIL_RATE: $FAIL_RATE"
echo "=================================================="

if perform_backup_with_retry "$BACKUP_PATH" "$MAX_RETRIES" "$RETRY_DELAY"; then
    echo ""
    echo "=================================================="
    echo "Job completed successfully at: $(date)"
    echo "=================================================="
    exit 0
else
    echo ""
    echo "=================================================="
    echo "Job failed at: $(date)"
    echo "=================================================="
    exit 1
fi


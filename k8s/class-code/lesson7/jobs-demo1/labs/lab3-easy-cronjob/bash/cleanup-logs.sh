#!/bin/bash
# Lab 3: Easy CronJob - Daily Log Cleanup
# Cleans up log files older than specified days

set -e

# Configuration from environment variables
LOG_DIR=${LOG_DIR:-/tmp/logs}
RETENTION_DAYS=${RETENTION_DAYS:-7}

echo "[$(date)] Starting log cleanup job..."
echo "Log directory: $LOG_DIR"
echo "Retention period: $RETENTION_DAYS days"

# Create log directory if it doesn't exist (for testing)
mkdir -p "$LOG_DIR"

# Calculate cutoff date (Unix timestamp) - handle both GNU and BSD date
if date -d "$RETENTION_DAYS days ago" &>/dev/null; then
    # GNU date (Linux)
    CUTOFF_TIMESTAMP=$(date -d "$RETENTION_DAYS days ago" +%s)
    CUTOFF_DATE=$(date -d "$RETENTION_DAYS days ago")
elif date -v-${RETENTION_DAYS}d &>/dev/null; then
    # BSD date (macOS)
    CUTOFF_TIMESTAMP=$(date -v-${RETENTION_DAYS}d +%s)
    CUTOFF_DATE=$(date -v-${RETENTION_DAYS}d)
else
    CUTOFF_TIMESTAMP=$(date +%s)
    CUTOFF_DATE=$(date)
fi

echo "Deleting files older than: $CUTOFF_DATE"

# Find and delete old log files using find with -mtime
deleted_count=0

# Use find with -mtime for simplicity (works on both Linux and macOS)
# Process files and count deletions
while IFS= read -r log_file; do
    if [ -f "$log_file" ]; then
        filename=$(basename "$log_file")
        file_date=$(stat -f %Sm "$log_file" 2>/dev/null || stat -c %y "$log_file" 2>/dev/null || echo "unknown")
        echo "  Found old file: $filename (modified: $file_date)"
        rm -f "$log_file"
        echo "    ✓ Deleted: $filename"
        deleted_count=$((deleted_count + 1))
    fi
done < <(find "$LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS 2>/dev/null)

if [ "$deleted_count" -gt 0 ]; then
    echo ""
    echo "=================================================="
    echo "Cleanup completed: $deleted_count file(s) deleted"
    echo "=================================================="
else
    echo ""
    echo "=================================================="
    echo "No old log files found to delete"
    echo "=================================================="
fi

echo ""
echo "[$(date)] Job completed successfully!"

exit 0


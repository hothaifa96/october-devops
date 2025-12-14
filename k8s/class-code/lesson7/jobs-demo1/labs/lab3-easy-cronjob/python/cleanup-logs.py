#!/usr/bin/env python3
"""
Lab 3: Easy CronJob - Daily Log Cleanup
Cleans up log files older than specified days
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration from environment variables
LOG_DIR = os.getenv('LOG_DIR', '/tmp/logs')
RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', '7'))

def cleanup_old_logs(log_dir, retention_days):
    """Remove log files older than retention_days"""
    print(f"[{datetime.now()}] Starting log cleanup job...")
    print(f"Log directory: {log_dir}")
    print(f"Retention period: {retention_days} days")
    
    log_path = Path(log_dir)
    
    # Create log directory if it doesn't exist (for testing)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    print(f"Deleting files older than: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Find old log files
    deleted_count = 0
    deleted_files = []
    
    # Look for .log files
    for log_file in log_path.glob('*.log'):
        try:
            # Get file modification time
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                print(f"  Found old file: {log_file.name} (modified: {file_mtime})")
                log_file.unlink()
                deleted_count += 1
                deleted_files.append(log_file.name)
                print(f"    ✓ Deleted: {log_file.name}")
        except Exception as e:
            print(f"    ✗ Error processing {log_file.name}: {str(e)}")
    
    # Summary
    print("\n" + "=" * 50)
    if deleted_count > 0:
        print(f"Cleanup completed: {deleted_count} file(s) deleted")
        print("Deleted files:")
        for filename in deleted_files:
            print(f"  - {filename}")
    else:
        print("No old log files found to delete")
    print("=" * 50)
    
    print(f"\n[{datetime.now()}] Job completed successfully!")
    return deleted_count

def create_sample_logs(log_dir):
    """Create sample log files for testing (optional)"""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create a few sample log files with different ages
    sample_files = [
        ('app-2024-01-01.log', 10),  # 10 days old
        ('app-2024-01-05.log', 6),   # 6 days old
        ('app-2024-01-10.log', 1),   # 1 day old
    ]
    
    for filename, days_ago in sample_files:
        file_path = log_path / filename
        file_path.write_text(f"Sample log content from {days_ago} days ago\n")
        # Set file modification time
        old_time = (datetime.now() - timedelta(days=days_ago)).timestamp()
        os.utime(file_path, (old_time, old_time))

def main():
    # For testing: create sample logs if LOG_DIR contains "test"
    if 'test' in LOG_DIR.lower():
        print("Creating sample log files for testing...")
        create_sample_logs(LOG_DIR)
        print("Sample logs created.\n")
    
    try:
        deleted_count = cleanup_old_logs(LOG_DIR, RETENTION_DAYS)
        return 0
    except Exception as e:
        print(f"\n✗ Error during cleanup: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())


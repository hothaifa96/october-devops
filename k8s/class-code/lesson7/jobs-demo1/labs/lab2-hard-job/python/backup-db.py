#!/usr/bin/env python3
"""
Lab 2: Hard Job - Database Backup with Retry Logic
Simulates database backup with retry mechanism and error handling
"""

import sys
import os
import time
import random
from datetime import datetime
from pathlib import Path

# Configuration from environment variables
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))
BACKUP_PATH = os.getenv('BACKUP_PATH', '/tmp/db_backup.sql')
FAIL_RATE = float(os.getenv('FAIL_RATE', '0.2'))  # 20% failure rate for testing

def simulate_backup(backup_path):
    """Simulate database backup operation"""
    print(f"Attempting to create backup at: {backup_path}")
    
    # Simulate potential failure
    if random.random() < FAIL_RATE:
        raise Exception("Database connection timeout - transient error")
    
    # Simulate backup operation
    time.sleep(1)
    
    # Create backup file
    backup_file = Path(backup_path)
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write mock backup data
    backup_data = f"-- Database Backup\n-- Created: {datetime.now()}\n-- Records: 1000\n"
    backup_file.write_text(backup_data)
    
    print(f"✓ Backup file created successfully")
    return backup_file

def validate_backup(backup_path):
    """Validate backup file exists and has content"""
    backup_file = Path(backup_path)
    
    if not backup_file.exists():
        raise Exception(f"Backup file not found: {backup_path}")
    
    if backup_file.stat().st_size == 0:
        raise Exception(f"Backup file is empty: {backup_path}")
    
    print(f"✓ Backup validation passed (size: {backup_file.stat().st_size} bytes)")
    return True

def perform_backup_with_retry(backup_path, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY):
    """Perform backup with retry logic"""
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n--- Attempt {attempt}/{max_retries} ---")
            
            # Perform backup
            backup_file = simulate_backup(backup_path)
            
            # Validate backup
            validate_backup(backup_path)
            
            print(f"\n✓ Backup completed successfully on attempt {attempt}")
            return True
            
        except Exception as e:
            last_error = e
            print(f"✗ Attempt {attempt} failed: {str(e)}")
            
            if attempt < max_retries:
                wait_time = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                print(f"  Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"\n✗ All {max_retries} attempts failed")
    
    raise Exception(f"Backup failed after {max_retries} attempts. Last error: {str(last_error)}")

def main():
    print("=" * 50)
    print("Database Backup Job")
    print(f"Started at: {datetime.now()}")
    print(f"Pod Name: {os.getenv('HOSTNAME', 'unknown')}")
    print("=" * 50)
    print(f"\nConfiguration:")
    print(f"  MAX_RETRIES: {MAX_RETRIES}")
    print(f"  RETRY_DELAY: {RETRY_DELAY}s")
    print(f"  BACKUP_PATH: {BACKUP_PATH}")
    print(f"  FAIL_RATE: {FAIL_RATE}")
    print("=" * 50)
    
    try:
        # Perform backup with retry logic
        perform_backup_with_retry(BACKUP_PATH, MAX_RETRIES, RETRY_DELAY)
        
        print("\n" + "=" * 50)
        print(f"Job completed successfully at: {datetime.now()}")
        print("=" * 50)
        return 0
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"Job failed: {str(e)}")
        print(f"Failed at: {datetime.now()}")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())


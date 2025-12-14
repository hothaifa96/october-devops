#!/usr/bin/env python3
"""
Python script for Kubernetes Job
This script performs a simple task and exits
"""

import sys
import time
import os
from datetime import datetime

def main():
    print(f"[{datetime.now()}] Starting Python job...")
    print(f"Job Name: {os.getenv('JOB_NAME', 'python-job')}")
    print(f"Pod Name: {os.getenv('HOSTNAME', 'unknown')}")
    
    # Simulate some work
    print("Processing data...")
    for i in range(5):
        print(f"  Step {i+1}/5 completed")
        time.sleep(1)
    
    # Example: Process some data
    data = [1, 2, 3, 4, 5]
    result = sum(x ** 2 for x in data)
    print(f"Calculation result: {result}")
    
    print(f"[{datetime.now()}] Job completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())


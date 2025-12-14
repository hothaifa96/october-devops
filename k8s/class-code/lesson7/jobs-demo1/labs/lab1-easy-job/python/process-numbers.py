#!/usr/bin/env python3
"""
Lab 1: Easy Job - Number Processing
Processes a list of numbers and calculates statistics
"""

import sys
from datetime import datetime

def main():
    print(f"[{datetime.now()}] Starting number processing job...")
    
    # Generate numbers from 1 to 100
    numbers = list(range(1, 101))
    print(f"Processing {len(numbers)} numbers...")
    
    # Calculate statistics
    total_sum = sum(numbers)
    average = total_sum / len(numbers)
    min_value = min(numbers)
    max_value = max(numbers)
    
    # Print results
    print("\n=== Results ===")
    print(f"Sum: {total_sum}")
    print(f"Average: {average}")
    print(f"Min: {min_value}")
    print(f"Max: {max_value}")
    print("===============")
    
    print(f"\n[{datetime.now()}] Job completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())


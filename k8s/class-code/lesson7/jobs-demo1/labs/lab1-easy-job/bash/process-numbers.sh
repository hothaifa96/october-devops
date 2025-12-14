#!/bin/bash
# Lab 1: Easy Job - Number Processing
# Processes a list of numbers and calculates statistics

set -e

echo "[$(date)] Starting number processing job..."

# Generate numbers from 1 to 100
numbers=($(seq 1 100))
count=${#numbers[@]}

echo "Processing $count numbers..."

# Calculate sum
sum=0
for num in "${numbers[@]}"; do
    sum=$((sum + num))
done

# Calculate average (using bc for floating point)
average=$(echo "scale=2; $sum / $count" | bc)

# Find min and max
min=${numbers[0]}
max=${numbers[0]}

for num in "${numbers[@]}"; do
    if [ $num -lt $min ]; then
        min=$num
    fi
    if [ $num -gt $max ]; then
        max=$num
    fi
done

# Print results
echo ""
echo "=== Results ==="
echo "Sum: $sum"
echo "Average: $average"
echo "Min: $min"
echo "Max: $max"
echo "==============="

echo ""
echo "[$(date)] Job completed successfully!"

exit 0


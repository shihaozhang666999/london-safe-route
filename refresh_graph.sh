#!/bin/bash

# Refresh London Safe Graph

echo "Starting to refresh the London safety graph..."

# Move to script's directory
cd "$(dirname "$0")"

# Step 1: Delete old files
python3 delete.py

# Step 2: Generate new graph
python3 services/generate_safety_graph.py

echo "London safety graph refresh complete!"

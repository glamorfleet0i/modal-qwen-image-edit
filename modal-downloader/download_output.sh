# !/bin/bash

# Activate the venv from ~/.venv
source ~/.venv/bin/activate

# If the output directory already exists, rename it to 'output_timestamp' where timestamp is the current timestamp
if [ -d "./output" ]; then
    mv ./output ./output_$(date +%s)
fi

# Download the output from the user-data volume
modal volume get user-data /output/12-29-2025
#!/bin/bash

IP=${1:-$IP}
PORT=${2:-$PORT}
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

# SSH into the remote server and create a zip archive of /root/comfy/ComfyUI/output
TS=$(date +%s)
zip_file="/root/comfy/export/ComfyUI_output_$TS.zip"
ssh -o StrictHostKeyChecking=no -p $PORT root@$IP "mkdir -p /root/comfy/export && cd /root/comfy/ComfyUI && zip -r $zip_file output"

# SFTP into the remote server and download the zip archive
sftp -o StrictHostKeyChecking=no -P $PORT root@$IP <<EOF
get $zip_file ./ComfyUI_output_$TS.zip
EOF

# Unzip using 7z on the downloaded zip file to ./comfy-output with -aou to auto rename existing files
cur_time=$(date +%Y-%m-%d_%H-%M-%S)
7z x ./ComfyUI_output_$TS.zip -o../comfy-output/$cur_time -aou

# Delete the downloaded zip file
rm ./ComfyUI_output_$TS.zip

echo "ComfyUI output downloaded successfully."

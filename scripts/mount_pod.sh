#!/bin/bash

IP=${1:-$IP}
PORT=${2:-$PORT}
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

OUTPUT_ONLY=${1:-false}
server_dir="/"
if [ "$OUTPUT_ONLY" = true ]; then
    server_dir="/root/comfy/ComfyUI/output"
fi

sshfs -o StrictHostKeyChecking=no -p $PORT root@$IP:$server_dir ~/mnt/quickpod
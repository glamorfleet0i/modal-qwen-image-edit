#!/bin/bash

IP=${1:-$IP}
PORT=${2:-$PORT}
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

OUTPUT_ONLY=${1:-true}
server_dir="/"
if [ "$OUTPUT_ONLY" = true ]; then
    server_dir="/root/comfy/ComfyUI/output"
fi

target=~/mnt/quickpod/qp-$IP-$PORT
mkdir -p $target
sshfs -o StrictHostKeyChecking=no -p $PORT root@$IP:$server_dir $target
echo "Mounted $IP:$PORT at '$target'"
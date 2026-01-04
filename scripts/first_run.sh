#!/bin/bash

# If no values are set, use the environment variables IP and PORT
IP=${1:-$IP}
PORT=${2:-$PORT}
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

# 1. Init pod
./run_init_pod.sh $IP $PORT

# 2. Run ComfyUI
./comfy_remote.sh $IP $PORT

# 3. Mount pod
# ./mount_pod.sh true $IP $PORT
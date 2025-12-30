#!/bin/bash

# Config
IP=""
PORT=""









# If no values are set, use the environment variables IP and PORT
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    IP=$SERVER_IP
    PORT=$SERVER_PORT
fi

if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

# 1. Init pod
./run_init_pod.sh $IP $PORT

# 2. Run ComfyUI
./comfy_remote.sh $IP $PORT

# 3. Mount pod
./run_mount_pod.sh true $IP $PORT
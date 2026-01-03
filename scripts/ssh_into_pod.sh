#!/bin/bash

IP=${1:-$IP}
PORT=${2:-$PORT}
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

ssh -o StrictHostKeyChecking=no -p $PORT root@$IP

#!/bin/bash

IP=$1
PORT=$2
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    IP=$SERVER_IP
    PORT=$SERVER_PORT
fi

if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

ssh -p $PORT root@$IP

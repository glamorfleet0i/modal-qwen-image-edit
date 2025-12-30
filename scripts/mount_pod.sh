#!/bin/bash

IP=$1
PORT=$2
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    IP=$SERVER_IP
    PORT=$SERVER_PORT
fi

sshfs -p $PORT root@$IP:/ ~/mnt/quickpod
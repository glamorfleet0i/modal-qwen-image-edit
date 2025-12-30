#!/bin/bash


# 1. Read IP and port of server from command line
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

# 2. Connect to the remote server and start/attach to tmux session
# We pass the command as an argument to ssh (instead of heredoc) to allow -t to allocate a TTY for tmux
CMD="
if tmux has-session -t comfyui 2>/dev/null; then
    echo 'Attaching to existing comfyui session...'
    tmux attach -t comfyui
else
    echo 'Starting new ComfyUI session...'
    tmux new-session -d -s comfyui 'bash -lc \"comfy launch -- --listen 0.0.0.0 --port 8000 --preview-method latent2rgb\"'
    tmux attach -t comfyui
fi
"

ssh -p $PORT -t root@$IP "$CMD"


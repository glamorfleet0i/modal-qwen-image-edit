#!/bin/bash


IP=${1:-$IP}
PORT=${2:-$PORT}

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
    tmux new-session -d -s comfyui 'bash -lc \"/root/comfy/start.sh\"'
    tmux attach -t comfyui
fi
"

ssh -o StrictHostKeyChecking=no -p $PORT -t root@$IP "$CMD"


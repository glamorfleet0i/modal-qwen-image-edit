#!/bin/bash

cmd="comfy launch -- --listen 0.0.0.0 --port 8000 --preview-method latent2rgb --use-sage-attention --enable-cors-header"

if tmux has-session -t comfyui 2>/dev/null; then
    echo 'A ComfyUI session is already active.'
else
    echo 'Starting new ComfyUI session...'
    tmux new-session -d -s comfyui $cmd
fi

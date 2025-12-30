#!/bin/bash

TS=$(date +%s)
INIT_FILES_ZIP=$1

# Extract the zipped init_files directory into /tmp/unix timestamp
unzip $INIT_FILES_ZIP -d /tmp/$TS

# For each folder name in /tmp/unix timestamp (not recursive, only at the root), delete it from /root/comfy/ComfyUI/ and copy it from /tmp/unix timestamp
for folder in /tmp/$TS/*; do
    echo "Processing folder: $(basename "$folder")"
    rm -rf /root/comfy/ComfyUI/$(basename "$folder")
    cp -r "$folder" /root/comfy/ComfyUI/
done

# Clean up temp files 
rm -rf /tmp/$TS
rm $INIT_FILES_ZIP

# Restart ComfyUI from tmux if it is running
if tmux has-session -t comfyui 2>/dev/null; then
    echo 'Restarting ComfyUI...'
    tmux kill-session -t comfyui
    tmux new-session -d -s comfyui 'bash -lc "comfy launch -- --listen 0.0.0.0 --port 8000 --preview-method latent2rgb"'
fi

echo 'Init files loaded successfully on server.'

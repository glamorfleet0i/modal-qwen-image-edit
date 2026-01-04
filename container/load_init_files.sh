#!/bin/bash
set -e

TS=$(date +%s)
INIT_FILES_ZIP=$1

if [ ! -f "$INIT_FILES_ZIP" ]; then
    echo "Error: Zip file '$INIT_FILES_ZIP' not found. Aborting."
    exit 1
fi

# Extract the zipped init_files directory into /tmp/unix timestamp
unzip $INIT_FILES_ZIP -d /tmp/$TS

# For each folder name in /tmp/unix timestamp (not recursive, only at the root), delete it from /root/comfy/ComfyUI/ and copy it from /tmp/unix timestamp
for folder in /tmp/$TS/*; do
    # SAFETY CHECK: If the glob didn't match anything, 
    # $folder will be the literal string "/tmp/.../*" which doesn't exist.
    # This check forces the loop to skip in that case.
    [ -e "$folder" ] || continue

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
    /root/comfy/start.sh
fi

touch /root/comfy/init_files_completed

echo 'Init files loaded successfully on server.'

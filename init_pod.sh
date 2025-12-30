#!/bin/bash

read -p "This will permanently remove existing files on the remote server (root@${1}:${2}) and replace them with the local files in ./init_files. Are you sure? Type Y or y to continue: " -n 1 -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# 1. Read IP and port of server from command line
IP=$1
PORT=$2

# 2. SFTP into server as root and remove the dirs:
# /root/comfy/ComfyUI/user/
# /root/comfy/ComfyUI/login/
# /root/comfy/ComfyUI/input/
#
# Then, copy all dirs recursively from ./init_files/ComfyUI to /root/comfy/ComfyUI/

sftp -P $PORT root@$IP <<EOF
rm -rf /root/comfy/ComfyUI/user/
rm -rf /root/comfy/ComfyUI/login/
rm -rf /root/comfy/ComfyUI/input/
put -r ./init_files/ComfyUI /root/comfy/ComfyUI/
EOF

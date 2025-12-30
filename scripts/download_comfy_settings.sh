#!/bin/bash

TS=$(date +%s)

# Backup the existing data in ./init_files/ComfyUI
if [ -d "./init_files/ComfyUI" ]; then
    mv ./init_files/ComfyUI ./init_files/ComfyUI_$TS
fi
    
IP=$1
PORT=$2
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    IP=$SERVER_IP
    PORT=$SERVER_PORT
fi

# SSH into the remote server and create a zip archive to /root/comfy/export/ComfyUI_$TS.zip
# - /root/comfy/ComfyUI/input
# - /root/comfy/ComfyUI/login
# - /root/comfy/ComfyUI/user
zip_file="/root/comfy/export/ComfyUI_$TS.zip"
ssh -p $PORT root@$IP "mkdir -p /root/comfy/export && cd /root/comfy/ComfyUI && zip -r $zip_file input login user"

# Download the zip file to ./init_files/ComfyUI_$TS.zip
sftp -P $PORT root@$IP <<EOF
get $zip_file ./init_files/ComfyUI_$TS.zip
EOF

# Remove ./init_files/ComfyUI
rm -rf ./init_files/ComfyUI

# Unzip the downloaded zip file to ./init_files/ComfyUI
unzip ./init_files/ComfyUI_$TS.zip -d ./init_files/ComfyUI

# Remove the downloaded zip file
rm ./init_files/ComfyUI_$TS.zip

echo "ComfyUI settings downloaded successfully."
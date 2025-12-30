#!/bin/bash

TS=$(date +%s)
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
# SSH into the remote server and create a zip archive of /root/comfy/ComfyUI/output. Only include files in the output directory, not /output in the root
zip_file="/root/comfy/export/ComfyUI_output_$TS.zip"
ssh -p $PORT root@$IP "mkdir -p /root/comfy/export && cd /root/comfy/ComfyUI && zip -r $zip_file output"

# SFTP into the remote server and download the zip archive
sftp -P $PORT root@$IP <<EOF
get $zip_file ./ComfyUI_output_$TS.zip
EOF

# Unzip using 7z on the downloaded zip file to ./comfy-output with -aou to auto rename existing files
7z x ./ComfyUI_output_$TS.zip -o../comfy-output -aou

# Delete the downloaded zip file
rm ./ComfyUI_output_$TS.zip

echo "ComfyUI output downloaded successfully."

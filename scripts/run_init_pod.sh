#!/bin/bash

IP=${1:-$IP}
PORT=${2:-$PORT}
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

read -p "This will permanently remove existing files on the remote server (root@${1}:${2}) and replace them with the local files in ./init_files. Are you sure? Type Y or y to continue: " -n 1 -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

TS=$(date +%s)
INIT_FILES_ZIP="init_files_$TS.zip"
# 1. Zip the init_files/ComfyUI directory and append the current unix timestamp
# The root should only have the ComfyUI directory
cd ./init_files/ComfyUI
zip -r ../../$INIT_FILES_ZIP .
cd ../..

# 2. SFTP into server as root and upload the zipped init_files directory to a temporary location
sftp -o StrictHostKeyChecking=no -P $PORT root@$IP <<EOF
put -r $INIT_FILES_ZIP /tmp/
EOF

# 3. SSH into server as root and run /root/comfy/load_init_files.sh
ssh -o StrictHostKeyChecking=no -p $PORT root@$IP "bash /root/comfy/load_init_files.sh /tmp/$INIT_FILES_ZIP"

# 4. Delete the local zipped init_files directory
rm $INIT_FILES_ZIP

echo "Init files uploaded and loaded successfully."
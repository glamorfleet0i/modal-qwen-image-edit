#!/bin/bash
set -e

IP=${1:-$IP}
PORT=${2:-$PORT}
if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "Error: IP or PORT not specified"
    exit 1
fi

cur_time=$(date +%Y-%m-%d_%H-%M-%S)
export_dir="/root/comfy/export"
output_archive_dir="/root/comfy/output_archive"
zip_file_name="ComfyUI_output_$cur_time.zip"

# Move /root/comfy/ComfyUI/output to /root/comfy/output_archive/$cur_time and zip it
commands="
mkdir -p $output_archive_dir/$cur_time
mv /root/comfy/ComfyUI/output $output_archive_dir/$cur_time
cd $output_archive_dir/$cur_time/output
zip -r $zip_file_name .
mkdir -p $export_dir
mv $output_archive_dir/$cur_time/output/$zip_file_name $export_dir
"
ssh -o StrictHostKeyChecking=no -p $PORT root@$IP $commands

# SFTP into the remote server and download the zip archive
sftp -o StrictHostKeyChecking=no -P $PORT root@$IP <<EOF
get $export_dir/$zip_file_name ./$zip_file_name
EOF

# Unzip using 7z on the downloaded zip file to ./comfy-output with -aou to auto rename existing files
7z x ./$zip_file_name -o../comfy-output/$cur_time -aou

# Delete the downloaded zip file
rm ./$zip_file_name

echo "ComfyUI output downloaded successfully."

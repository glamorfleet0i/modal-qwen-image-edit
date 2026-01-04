# !/bin/bash

volume_name="user-data"
remote_path="/output"
local_dest="/home/kevin/Projects/modal/comfyui-qwen-image-edit/modal-downloader/out/$(date +%Y-%m-%d_%H-%M-%S)"

source ~/.venv/bin/activate
mkdir -p $local_dest
modal volume get $volume_name $remote_path $local_dest
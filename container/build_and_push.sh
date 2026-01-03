#!/bin/bash
set -e

docker build -t cloud-comfyui-qwen-image-edit .
docker tag cloud-comfyui-qwen-image-edit:latest glamorfleet0i/cloud-comfyui-qwen-image-edit:latest
docker push glamorfleet0i/cloud-comfyui-qwen-image-edit:latest
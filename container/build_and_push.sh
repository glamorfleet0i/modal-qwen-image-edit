#!/bin/bash
set -e

docker build -t cloud-comfyui-universal .
docker tag cloud-comfyui-universal:latest glamorfleet0i/cloud-comfyui-universal:latest
docker push glamorfleet0i/cloud-comfyui-universal:latest
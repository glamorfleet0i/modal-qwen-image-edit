#!/bin/bash

if ! grep -qF "$SSH_PUB_KEY" ~/.ssh/authorized_keys; then
  echo "$SSH_PUB_KEY" >> ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
  echo "[Added user SSH public key to authorized_keys.]"
fi

ln -s /root/comfy/ComfyUI/output /quickpod/output

python /root/comfy/download_models.py

#!/bin/bash

# If there is not a file called "setup_complete" in /root/comfy, run setup
if [ ! -f /root/comfy/setup_complete ]; then
  set -e
  
  if ! grep -qF "$SSH_PUB_KEY" ~/.ssh/authorized_keys; then
    echo "$SSH_PUB_KEY" >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    echo "[Added user SSH public key to authorized_keys.]"
    service ssh restart
  fi

  python /root/comfy/download_models.py

  touch /root/comfy/setup_complete
fi

# Wait forever to keep container alive
tail -f /dev/null
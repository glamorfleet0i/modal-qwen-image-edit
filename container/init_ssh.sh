#!/bin/bash
set -e

mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Generate system host keys if not already present
host_key_files=(
    /etc/ssh/ssh_host_rsa_key
    /etc/ssh/ssh_host_ecdsa_key
    /etc/ssh/ssh_host_ed25519_key
)

for file in "${host_key_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "[Generating SSH Host Keys...]"
        ssh-keygen -A
        if [[ $? -eq 0 ]]; then # Ensure successful key generation
            echo "[SSH Host Keys successfully generated.]"
        else
            echo "[Error generating SSH Host Keys! Exiting...]"
            exit 1
        fi
        break
    fi
done

# Run on startup
systemctl enable ssh

# Start the SSH service
service ssh start

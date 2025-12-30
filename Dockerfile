FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    HF_XET_HIGH_PERFORMANCE=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    "fastapi[standard]==0.115.4" \
    "comfy-cli==1.5.3" \
    "huggingface-hub==0.36.0" \
    "hf_transfer"

# Set working directory for ComfyUI installation
WORKDIR /root/comfy

# Install ComfyUI and dependencies
RUN comfy --skip-prompt install --fast-deps --nvidia

# Install custom nodes
RUN comfy node install --fast-deps login

# Add download models script
COPY download_models.py /root/comfy/download_models.py

# Update system and install openssh
RUN apt-get update && apt-get full-upgrade -y && apt-get install openssh-server -y

# Set up ssh access
COPY init_ssh.sh /root/comfy/init_ssh.sh
RUN chmod +x /root/comfy/init_ssh.sh && /root/comfy/init_ssh.sh

# Copy sshd_config
COPY sshd_config /etc/ssh/sshd_config
RUN chmod 600 /etc/ssh/sshd_config

# Install other items
RUN apt-get install tmux htop vim zip -y

# Add start script
COPY start.sh /root/comfy/start.sh
RUN chmod +x /root/comfy/start.sh

# Add boot script
COPY boot.sh /root/comfy/boot.sh
RUN chmod +x /root/comfy/boot.sh

# Expose ports
EXPOSE 8000
EXPOSE 48213

# Keep container alive
CMD ["tail", "-f", "/dev/null"]

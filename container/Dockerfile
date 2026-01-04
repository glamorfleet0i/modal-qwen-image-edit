FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    HF_XET_HIGH_PERFORMANCE=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1

# Install required system dependencies for ComfyUI installation
RUN apt-get update && apt-get full-upgrade -y && apt-get install -y --no-install-recommends \
    git \
    openssh-server \
    tmux \
    htop \
    vim \
    zip \
    unzip

# Install Python dependencies
RUN pip install --no-cache-dir \
    "fastapi[standard]==0.115.4" \
    "comfy-cli==1.5.3" \
    "huggingface_hub[cli]" \
    "hf_transfer" \
    "hf_xet"

RUN pip config set global.extra-index-url https://download.pytorch.org/whl/cu128

# Install ComfyUI
WORKDIR /root/comfy
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /root/comfy/ComfyUI
RUN uv pip install -r requirements.txt --system
# Manually install ComfyUI-Manager
WORKDIR /root/comfy/ComfyUI/custom_nodes
RUN git clone https://github.com/Comfy-Org/ComfyUI-Manager.git
WORKDIR /root/comfy/ComfyUI/custom_nodes/ComfyUI-Manager
RUN uv pip install -r requirements.txt --system
# Install SageAttention 2 Wheel
COPY sageattention-2.2.0-cp312-cp312-linux_x86_64.whl /root/comfy
RUN uv pip install /root/comfy/sageattention-2.2.0-cp312-cp312-linux_x86_64.whl --system
# Setup Comfy CLI
WORKDIR /root/comfy/ComfyUI
RUN comfy --skip-prompt set-default /root/comfy/ComfyUI
RUN comfy tracking disable
RUN comfy node install --fast-deps login

# Install build essential (required for SageAttention 2)
RUN apt-get install -y build-essential

# Remove placeholder output file
RUN rm /root/comfy/ComfyUI/output/_output_images_will_be_put_here

# Set up ssh access
COPY init_ssh.sh /root/comfy/init_ssh.sh
RUN chmod +x /root/comfy/init_ssh.sh && /root/comfy/init_ssh.sh
COPY sshd_config /etc/ssh/sshd_config
RUN chmod 600 /etc/ssh/sshd_config

# Copy scripts
COPY start.sh /root/comfy/start.sh
RUN chmod +x /root/comfy/start.sh
COPY boot.sh /root/comfy/boot.sh
RUN chmod +x /root/comfy/boot.sh
COPY load_init_files.sh /root/comfy/load_init_files.sh
RUN chmod +x /root/comfy/load_init_files.sh
COPY download_models.py /root/comfy/download_models.py

# Expose ports
EXPOSE 8000
EXPOSE 48213

# Run boot script
ENTRYPOINT ["/root/comfy/boot.sh"]

#!/bin/bash
set -e

# Run as script
export DEBIAN_FRONTEND=noninteractive

apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common gnupg tzdata tmux htop git && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip

mkdir -p /sage_builder
cd /sage_builder

python3.12 -m venv venv
source venv/bin/activate

pip install build wheel
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128



# Run manually when ready
source venv/bin/activate
git clone https://github.com/thu-ml/SageAttention.git
cd SageAttention 
export TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;12.0"
export EXT_PARALLEL=4 NVCC_APPEND_FLAGS="--threads 8" MAX_JOBS=32
python setup.py bdist_wheel
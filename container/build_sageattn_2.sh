#!/bin/bash
set -e

source /root/comfy/venv/bin/activate
git clone https://github.com/thu-ml/SageAttention.git
cd SageAttention 
export EXT_PARALLEL=4 NVCC_APPEND_FLAGS="--threads 8" MAX_JOBS=32
python setup.py bdist_wheel
#!/bin/bash

# 1.Install ComfyUI
mkdir -p /kaggle/working/comfy
cd /kaggle/working/comfy
git clone https://github.com/comfyanonymous/ComfyUI.git
cd /kaggle/working/comfy/ComfyUI/
uv pip install -r requirements.txt

# 3. Download VAE and dependencies
uv pip install huggingface-hub hf_transfer py7zr
HF_HUB_ENABLE_HF_TRANSFER=1 HF_XET_HIGH_PERFORMANCE=1 hf download Comfy-Org/Qwen-Image_ComfyUI split_files/vae/qwen_image_vae.safetensors --local-dir /kaggle/working/comfy/ComfyUI/models/vae/
mv /kaggle/working/comfy/ComfyUI/models/vae/split_files/vae/qwen_image_vae.safetensors /kaggle/working/comfy/ComfyUI/models/vae
rm -rf /kaggle/working/comfy/ComfyUI/models/vae/split_files

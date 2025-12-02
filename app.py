import json
import subprocess
import uuid
from pathlib import Path
from typing import Dict

import modal
import modal.experimental

image = (  # build up a Modal Image to run ComfyUI, step by step
    modal.Image.debian_slim(  # start from basic Linux with Python
        python_version="3.12"
    )
    .apt_install("git")  # install git to clone ComfyUI
    .uv_pip_install("fastapi[standard]==0.115.4")  # install web dependencies
    .uv_pip_install("comfy-cli==1.5.3")  # install comfy-cli
    .run_commands(  # use comfy-cli to install ComfyUI and its dependencies
        "comfy --skip-prompt install --fast-deps --nvidia"
    )
)

def hf_download():
    import os
    from huggingface_hub import hf_hub_download

    MODELS = {
        "vae": {
            "repo_id": "Comfy-Org/Qwen-Image_ComfyUI",
            "filename": "split_files/vae/qwen_image_vae.safetensors",
            "dest": "/root/comfy/ComfyUI/models/vae/qwen_image_vae.safetensors",
        },
        "qwen_edit": {
            "repo_id": "Comfy-Org/Qwen-Image-Edit_ComfyUI",
            "filename": "split_files/diffusion_models/qwen_image_edit_fp8_e4m3fn.safetensors",
            "dest": "/root/comfy/ComfyUI/models/checkpoints/qwen_image_edit_fp8_e4m3fn.safetensors",
        },
        "text_encoder": {
            "repo_id": "Comfy-Org/Qwen-Image_ComfyUI",
            "filename": "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "dest": "/root/comfy/ComfyUI/models/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        },
        "lightning": {
            "repo_id": "lightx2v/Qwen-Image-Lightning",
            "filename": "Qwen-Image-Lightning-4steps-V1.0.safetensors",
            "dest": "/root/comfy/ComfyUI/models/checkpoints/Qwen-Image-Lightning-4steps-V1.0.safetensors",
        }
    }

    for model_name, model_info in MODELS.items():
        print(f"Downloading {model_name}...")
        model_path = hf_hub_download(
            repo_id=model_info["repo_id"],
            filename=model_info["filename"],
            cache_dir="/cache",
        )
        dest_path = model_info["dest"]
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        print(f"Symlinking {model_path} to {dest_path}")
        subprocess.run(
            f"ln -s {model_path} {dest_path}",
            shell=True,
            check=True,
        )


vol = modal.Volume.from_name("hf-hub-cache", create_if_missing=True)

image = (
    # install huggingface_hub with hf_xet support to speed up downloads
    image.uv_pip_install("huggingface-hub==0.36.0")
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
    .run_function(
        hf_download,
        # persist the HF cache to a Modal Volume so future runs don't re-download models
        volumes={"/cache": vol},
    )
)

app = modal.App(name="example-comfyapp", image=image)


@app.function(
    max_containers=1,  # limit interactive session to 1 container
    # gpu="L40S",  # good starter GPU for inference
    volumes={"/cache": vol},  # mounts our cached models
)
@modal.concurrent(
    max_inputs=10
)  # required for UI startup process which runs several API calls concurrently
@modal.web_server(8000, startup_timeout=60)
def ui():
    subprocess.Popen("comfy launch -- --listen 0.0.0.0 --port 8000", shell=True)
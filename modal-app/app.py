import json
import subprocess
import uuid
from pathlib import Path
from typing import Dict

import modal
import modal.experimental

image = (
    modal.Image.debian_slim(python_version="3.12")
    # Install core system packages
    .apt_install("git", "build-essential")
    # Install python deps
    .uv_pip_install("fastapi[standard]==0.115.4", "comfy-cli==1.5.3")
    # Install ComfyUI
    .run_commands("comfy --skip-prompt install --fast-deps --nvidia")
    # Install custom nodes
    .run_commands("comfy node install --fast-deps login")
    # Update to PyTorch CUDA 12.8
    .run_commands("uv pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --system")
    # Add SageAttention 2 Wheel
    .add_local_file('sageattention-2.2.0-cp312-cp312-linux_x86_64.whl', remote_path='/root/comfy/ComfyUI/sageattention-2.2.0-cp312-cp312-linux_x86_64.whl', copy=True)
    .uv_pip_install('/root/comfy/ComfyUI/sageattention-2.2.0-cp312-cp312-linux_x86_64.whl')
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
        "qwen_image_edit_2509_fp8": {
            "repo_id": "Comfy-Org/Qwen-Image-Edit_ComfyUI",
            "filename": "split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors",
            "dest": "/root/comfy/ComfyUI/models/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors",
        },
        "qwen_image_edit_2509_fp8_scaled": {
            "repo_id": "lightx2v/Qwen-Image-Lightning",
            "filename": "Qwen-Image-Edit-2509/qwen_image_edit_2509_fp8_e4m3fn_scaled.safetensors",
            "dest": "/root/comfy/ComfyUI/models/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn_scaled.safetensors",
        },
        "text_encoder": {
            "repo_id": "Comfy-Org/Qwen-Image_ComfyUI",
            "filename": "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "dest": "/root/comfy/ComfyUI/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        },
        "lightning_2509_4step": {
            "repo_id": "lightx2v/Qwen-Image-Lightning",
            "filename": "Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
            "dest": "/root/comfy/ComfyUI/models/loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
        },
        "lightning_2509_8step": {
            "repo_id": "lightx2v/Qwen-Image-Lightning",
            "filename": "Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors",
            "dest": "/root/comfy/ComfyUI/models/loras/Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors",
        },
        "qwen_image_edit_2511_fused_4step": {
            "repo_id": "lightx2v/Qwen-Image-Edit-2511-Lightning",
            "filename": "qwen_image_edit_2511_fp8_e4m3fn_scaled_lightning_comfyui.safetensors",
            "dest": "/root/comfy/ComfyUI/models/diffusion_models/qwen_image_edit_2511_fp8_e4m3fn_scaled_lightning_comfyui.safetensors",
        },
        "snofs": {
            "repo_id": "glamorfleet/pub-models",
            "filename": "40d031c3-a791-4159-a2b2-9ed2b3164c70.safetensors",
            "dest": "/root/comfy/ComfyUI/models/loras/Qwen_Snofs_1_3.safetensors"
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

def symlink_user_data():
    import os
    import shutil

    # These are the directories we want to persist between runs.
    # The key is the directory within the ComfyUI installation.
    # The value is the corresponding directory in our persistent volume.
    linked_dirs_map = {
        "/root/comfy/ComfyUI/user": "/persisted-user-data/user",
        "/root/comfy/ComfyUI/input": "/persisted-user-data/input",
        "/root/comfy/ComfyUI/output": "/persisted-user-data/output",
        "/root/comfy/ComfyUI/login": "/persisted-user-data/login",
    }

    for link_name, target in linked_dirs_map.items():
        print(f"Symlinking {link_name} -> {target}")

        # If the original path is a directory, handle it as such.
        if os.path.isdir(link_name) and not os.path.islink(link_name):
            print(f"{link_name} is a directory. Applying directory symlink logic.")
            os.makedirs(target, exist_ok=True) # Ensure target directory exists.

            # Only copy contents if the target directory is empty.
            if not os.listdir(target):
                print(f"Target {target} is empty. Moving contents from {link_name}.")
                shutil.copytree(link_name, target, dirs_exist_ok=True)
            else:
                print(f"Target {target} has content. Skipping copy.")

            shutil.rmtree(link_name)
            os.symlink(target, link_name)

        # If the original path is a file, handle it.
        elif os.path.isfile(link_name) and not os.path.islink(link_name):
            print(f"{link_name} is a file. Applying file symlink logic.")
            os.makedirs(os.path.dirname(target), exist_ok=True) # Ensure parent of target file exists.

            # Only copy the file if the target doesn't already exist.
            if not os.path.exists(target):
                print(f"Target {target} does not exist. Copying from {link_name}.")
                shutil.copy2(link_name, target)
            else:
                print(f"Target {target} already exists. Skipping copy.")

            os.remove(link_name)
            os.symlink(target, link_name)

        elif not os.path.exists(link_name) and not os.path.islink(link_name):
            print(f"Warning: {link_name} does not exist, but creating symlink to {target}.")
            os.symlink(target, link_name)

vol_model_cache = modal.Volume.from_name("hf-hub-cache", create_if_missing=True)
vol_user_data = modal.Volume.from_name("user-data", create_if_missing=True)

image = (
    # install huggingface_hub with hf_xet support to speed up downloads
    image.uv_pip_install("huggingface-hub==0.36.0")
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
    .run_function(
        hf_download,
        # persist the HF cache to a Modal Volume so future runs don't re-download models
        volumes={"/cache": vol_model_cache},
    )
    .run_function(
        symlink_user_data,
        # persist user data written to the transient boot disk
        volumes={"/persisted-user-data": vol_user_data},
    )
)

image = (
    # Install custom nodes
    image.run_commands("comfy node install --fast-deps ComfyUI-KJNodes")
)
app = modal.App(name="comfyui-qwen-image-edit", image=image)


@app.function(
    max_containers=1,
    # Recommended GPUs:
    # - L4 (24GB, $0.80/hr)
    # - A10 (24GB, $1.10/hr)
    # - L40S (48GB, $1.95/hr)
    # - A100-40GB (40GB, $2.10/hr)
    gpu="A10",
    volumes={"/cache": vol_model_cache, "/persisted-user-data": vol_user_data},
    # enable_memory_snapshot=True,
    # experimental_options={"enable_gpu_snapshot": True}
)
@modal.concurrent(
    max_inputs=10
)  # required for UI startup process which runs several API calls concurrently
@modal.web_server(8000, startup_timeout=60)
def ui():
    subprocess.Popen("comfy launch -- --listen 0.0.0.0 --port 8000 --use-sage-attention --preview-method latent2rgb", shell=True)
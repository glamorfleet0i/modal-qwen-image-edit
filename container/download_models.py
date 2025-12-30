import os
import shutil
from huggingface_hub import hf_hub_download

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

MODELS = {
    "vae": {
        "repo_id": "Comfy-Org/Qwen-Image_ComfyUI",
        "filename": "split_files/vae/qwen_image_vae.safetensors",
        "dest": "/root/comfy/ComfyUI/models/vae/qwen_image_vae.safetensors",
    },
    "text_encoder": {
        "repo_id": "Comfy-Org/Qwen-Image_ComfyUI",
        "filename": "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        "dest": "/root/comfy/ComfyUI/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
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
    path_without_filename = os.path.dirname(model_info["dest"])
    cached_path = hf_hub_download(
        repo_id=model_info["repo_id"],
        filename=model_info["filename"],
        local_dir=path_without_filename,
        local_dir_use_symlinks=False
    )

    # If the filename has paths, remove them and move them to the dest folder
    if "/" in model_info["filename"]:
        filename = model_info["filename"].split("/")[-1]
        os.makedirs(path_without_filename, exist_ok=True)
        shutil.move(cached_path, path_without_filename)

    print(f"Downloaded to {cached_path}")
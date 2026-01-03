import os
import shutil
from huggingface_hub import hf_hub_download

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"

MODELS = {
    "qwen_image_vae": {
        "repo_id": "Comfy-Org/Qwen-Image_ComfyUI",
        "repo_path": "split_files/vae/qwen_image_vae.safetensors",
        "local_dest": "/root/comfy/ComfyUI/models/vae/qwen_image_vae.safetensors",
    },
    "qwen_image_text_encoder": {
        "repo_id": "Comfy-Org/Qwen-Image_ComfyUI",
        "repo_path": "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        "local_dest": "/root/comfy/ComfyUI/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
    },
    "qwen_image_edit_2511_fused_4step": {
        "repo_id": "lightx2v/Qwen-Image-Edit-2511-Lightning",
        "repo_path": "qwen_image_edit_2511_fp8_e4m3fn_scaled_lightning_comfyui.safetensors",
        "local_dest": "/root/comfy/ComfyUI/models/diffusion_models/qwen_image_edit_2511_fp8_e4m3fn_scaled_lightning_comfyui.safetensors",
    },
    # "snofs": {
    #     "repo_id": "glamorfleet/pub-models",
    #     "repo_path": "40d031c3-a791-4159-a2b2-9ed2b3164c70.safetensors",
    #     "dest": "/root/comfy/ComfyUI/models/loras/Qwen_Snofs_1_3.safetensors"
    # }
}

# Warn if hf transfer or hf xet are not installed in py env
try:
    import hf_transfer
    print("hf_transfer detected.")
except ImportError:
    print("Warning: hf_transfer is not installed. Performance may be reduced.")

try:
    import hf_xet
    print("hf_xet detected.")
except ImportError:
    print("Warning: hf_xet is not installed. Performance may be reduced.")


for model_name, model_info in MODELS.items():
    try:
        if os.path.exists(model_info["local_dest"]):
            print(f"\nModel '{model_name}' already exists at '{model_info['local_dest']}'. Skipping download.")
            continue

        print(f"\nDownloading '{model_name}' to '{model_info['local_dest']}'...")
        target_filename = os.path.basename(model_info["local_dest"])
        target_dest = os.path.dirname(model_info["local_dest"])
        downloaded_path = hf_hub_download(
            repo_id=model_info["repo_id"],
            filename=model_info["repo_path"],
            local_dir=target_dest
        )
        print(f"Successfully downloaded to '{downloaded_path}'.")

        # If the repo name has paths, it downloaded to its subfolder and we need to move it to the target dest and remove the extra folders.
        # e.g. after moving model.safetensors
        # from /root/comfy/ComfyUI/models/diffusion_models/split_files/diffusion_models/model.safetensors
        # to /root/comfy/ComfyUI/models/diffusion_models/model.safetensors
        # delete the entire /root/comfy/ComfyUI/models/diffusion_models/split_files folder
        if "/" in model_info["repo_path"]:
            # Move the model first
            target_dest_filename = os.path.join(target_dest, target_filename)
            os.rename(downloaded_path, target_dest_filename)
            print(f"Moved downloaded model to '{target_dest_filename}'.")
            # Remove the root of the extra dirs
            extra_dirs_root = model_info["repo_path"].split("/")[0]
            extra_dirs_root_path = os.path.join(target_dest, extra_dirs_root)
            shutil.rmtree(extra_dirs_root_path)
            print(f"Removed extra dirs at '{extra_dirs_root_path}'.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to download '{model_name}'!")
